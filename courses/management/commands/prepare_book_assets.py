"""Prepare protected audio and only the PDF pages referenced by reviewed data."""
import hashlib
import json
import re
import shutil
import subprocess
import tempfile
import zipfile
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path, PurePosixPath

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError


SOURCES = {
    (1, 'course'): (
        'english_for_everyone_level_1_course_book_beginner.pdf',
        '467_2_English_for_Everyone_Level_1_Beginner_Course_Book_2016_Audio.zip',
    ),
    (1, 'practice'): (
        'English_for_Everyone_-_Level_1_Beginner_-_Practice_Book.pdf',
        '467_4_English_for_Everyone_Level_1_Beginner_Practice_Book_2016_Audio.zip',
    ),
    (2, 'course'): (
        'English_for_Everyone_Level_2_Beginner_Course_Book_by_Rachel_Harding.pdf',
        'Level+2+Course+Beginner.zip',
    ),
    (2, 'practice'): (
        'dk_english_for_everyone_level_2_beginner_practice_book.pdf',
        'Level+2+Practice+Beginner.zip',
    ),
}


def walk_strings(value):
    if isinstance(value, str):
        yield value
    elif isinstance(value, list):
        for item in value:
            yield from walk_strings(item)
    elif isinstance(value, dict):
        for item in value.values():
            yield from walk_strings(item)


class Command(BaseCommand):
    help = 'Extract namespaced book audio and render referenced pages offline; never access the database.'

    def add_arguments(self, parser):
        parser.add_argument('--audio-only', action='store_true')
        parser.add_argument('--pages-only', action='store_true')
        parser.add_argument('--manifest', action='append')

    def handle(self, *args, **options):
        root = Path(settings.BASE_DIR)
        if not options['pages_only']:
            for (level, book), (_, archive_name) in SOURCES.items():
                archive_path = root / 'books' / archive_name
                if not archive_path.is_file():
                    raise CommandError(f'Archive missing: {archive_path}')
                destination = root / 'static/audio/books' / f'level{level}' / book
                added = existing = 0
                with zipfile.ZipFile(archive_path) as archive:
                    for member in archive.infolist():
                        parts = PurePosixPath(member.filename).parts
                        if '__MACOSX' in parts or any(part.startswith('.') for part in parts):
                            continue
                        if not member.filename.lower().endswith('.mp3'):
                            continue
                        first_unit = next((index for index, part in enumerate(parts) if part.isdigit()), None)
                        if first_unit is None:
                            continue
                        relative = Path(*parts[first_unit:])
                        target = (destination / relative).resolve()
                        if not target.is_relative_to(destination.resolve()):
                            raise CommandError(f'Unsafe archive path: {member.filename}')
                        data = archive.read(member)
                        if target.exists():
                            if hashlib.sha256(target.read_bytes()).digest() != hashlib.sha256(data).digest():
                                raise CommandError(f'Audio content collision: {target}')
                            existing += 1
                            continue
                        target.parent.mkdir(parents=True, exist_ok=True)
                        target.write_bytes(data)
                        added += 1
                self.stdout.write(f'Level {level} {book}: {added} audio files prepared, {existing} unchanged')
        if options['audio_only']:
            return

        manifests = options['manifest'] or [
            str(root / 'courses/data/book_enrichment_v2/level1.json'),
            str(root / 'courses/data/book_enrichment_v2/level2.json'),
        ]
        pages = set()
        concat_tasks = []
        for filename in manifests:
            data = json.loads(Path(filename).read_text(encoding='utf-8'))
            for value in walk_strings(data):
                match = re.fullmatch(r'/static/coursebooks/level([12])/(course|practice)/page-(\d+)\.jpg', value)
                if match:
                    pages.add((int(match[1]), match[2], int(match[3]), value))
            for lesson in data.get('lessons', []):
                for exercise in lesson.get('exercises', []):
                    sources = (exercise.get('content') or {}).get('provenance', {}).get('audio_concat_sources')
                    if sources:
                        concat_tasks.append((exercise.get('audio_url'), sources))

        for destination_url, sources in concat_tasks:
            if not re.fullmatch(r'/static/audio/books/level[12]/(?:course|practice)/\d+/[\w-]+_combined\.mp3', str(destination_url)):
                raise CommandError(f'Unsafe combined audio destination: {destination_url}')
            target = root / destination_url.lstrip('/')
            inputs = []
            hashes = []
            for url in sources:
                if not str(url).startswith('/static/audio/books/'):
                    raise CommandError(f'Invalid concatenation source: {url}')
                source = (root / url.lstrip('/')).resolve()
                if not source.is_relative_to((root / 'static/audio/books').resolve()) or not source.is_file():
                    raise CommandError(f'Missing concatenation source: {url}')
                inputs.append(source)
                hashes.append(hashlib.sha256(source.read_bytes()).hexdigest())
            signature = hashlib.sha256(json.dumps([sources, hashes]).encode()).hexdigest()
            marker = target.with_suffix('.concat.sha256')
            if target.is_file() and marker.is_file() and marker.read_text().strip() == signature:
                continue
            if target.exists() and not marker.is_file():
                raise CommandError(f'Untracked audio collision: {target}')
            with tempfile.TemporaryDirectory(prefix='lrnen-book-audio-') as temp:
                output = Path(temp) / 'combined.mp3'
                arguments = ['ffmpeg', '-hide_banner', '-loglevel', 'error', '-y']
                for source in inputs:
                    arguments.extend(['-i', str(source)])
                streams = ''.join(f'[{index}:a]' for index in range(len(inputs)))
                arguments.extend([
                    '-filter_complex', f'{streams}concat=n={len(inputs)}:v=0:a=1[out]',
                    '-map', '[out]', '-codec:a', 'libmp3lame', '-q:a', '4', str(output),
                ])
                subprocess.run(arguments, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE, timeout=120)
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(output, target)
                marker.write_text(signature + '\n')
            self.stdout.write(f'Combined {len(inputs)} contextual audio clips: {destination_url}')

        def render(item):
            level, book, number, url = item
            target = root / url.lstrip('/')
            if target.is_file():
                return False
            target.parent.mkdir(parents=True, exist_ok=True)
            subprocess.run([
                'pdftoppm', '-f', str(number), '-l', str(number), '-scale-to', '1800',
                '-jpeg', '-jpegopt', 'quality=88', '-singlefile',
                str(root / 'books' / SOURCES[level, book][0]), str(target.with_suffix('')),
            ], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
            return True

        with ThreadPoolExecutor(max_workers=3) as pool:
            added_pages = sum(pool.map(render, sorted(pages)))
        self.stdout.write(self.style.SUCCESS(f'{added_pages} PDF pages prepared; {len(pages)} referenced pages checked'))
