"""Repair the 32 Book 1 exercises imported without correct answer indices."""
import json
import re
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction


# These six rows were generated later from incomplete text, have no matching
# source audio, and duplicate valid Unit 22 material already in the database.
CORRUPT_UNIT_22_ORDERS = {9, 10, 11, 12, 13, 14}

MISSING_AUDIO = {
    (24, 'LISTEN TO THE AUDIO AND MATCH THE TWO PLACES THAT THE SPEAKER DESCRIBES'):
        '/static/audio/24/24_2_1.mp3',
    (25, 'LISTEN TO THE AUDIO AND ANSWER THE QUESTIONS'):
        '/static/audio/25/25_5.mp3',
    (37, 'LISTEN TO THE AUDIO AND ANSWER THE QUESTIONS'):
        '/static/audio/37/37_7_1.mp3',
    (40, 'LISTEN TO THE AUDIO AND CHOOSE THE CORRECT ANSWERS'):
        '/static/audio/40/40_2.mp3',
}


def rows_for(exercise):
    content = exercise.content or {}
    return content.get('questions') or content.get('sentences') or []


def has_missing_correct(exercise):
    return any(
        isinstance(row, dict)
        and isinstance(row.get('options'), list)
        and row.get('correct', row.get('correct_index')) is None
        for row in rows_for(exercise)
    )


def mark_first_example(exercise):
    """Persist the UI convention: row one is a guided example when work follows."""
    content = dict(exercise.content or {})
    key = next((name for name in ('questions', 'sentences') if isinstance(content.get(name), list)), None)
    if not key or len(content[key]) < 2:
        return False
    updated = [
        ({**row, 'is_example': True} if index == 0 else row)
        if isinstance(row, dict) else row
        for index, row in enumerate(content[key])
    ]
    if updated == content[key]:
        return False
    content[key] = updated
    exercise.content = content
    exercise.save(update_fields=['content'])
    return True


def local_path(url):
    if not url or not url.startswith('/static/'):
        return None
    path = Path(settings.BASE_DIR) / url.removeprefix('/')
    return path if path.exists() else None


def sibling_audio_urls(url, expected_count):
    """Expand ..._1.mp3 to one clip per row when all clips exist."""
    path = local_path(url)
    if not path:
        return []
    match = re.fullmatch(r'(.+)_1(\.mp3)', path.name, re.IGNORECASE)
    if not match or expected_count < 2:
        return [url]
    prefix, extension = match.groups()
    candidates = [path.with_name(f'{prefix}_{index}{extension}') for index in range(1, expected_count + 1)]
    if not all(candidate.exists() for candidate in candidates):
        return [url]
    return [f"/static/audio/{candidate.relative_to(Path(settings.BASE_DIR) / 'static' / 'audio').as_posix()}" for candidate in candidates]


def special_case_content(exercise):
    """Restore the five answerable rows visible on Book 1 page 78."""
    if exercise.lesson.order != 24 or 'TWO PLACES' not in exercise.instruction.upper():
        return dict(exercise.content or {})
    options = ['restaurant', 'mosque', 'movie theater', 'church', 'hospital', 'supermarket']
    return {
        'questions': [
            {'question': f'Which place is described in audio {index}?', 'options': options, 'correct': None}
            for index in range(1, 6)
        ],
        'image_url': (
            '/static/book/'
            'English_for_Everyone_-_Level_1_Beginner_-_Practice_Book_page-0078.jpg'
        ),
    }


class Command(BaseCommand):
    help = 'Book 1 dagi correct=null bo‘lgan 32 nosoz topshiriqni ta’mirlaydi'

    def add_arguments(self, parser):
        parser.add_argument('--dry-run', action='store_true')
        parser.add_argument('--workers', type=int, default=4)
        parser.add_argument('--delay', type=float, default=0)

    def handle(self, *args, **options):
        from decouple import config as env
        from google import genai
        from google.genai import types

        from quiz.models import Exercise

        queryset = Exercise.objects.filter(
            lesson__title__startswith='[Book 1]'
        ).select_related('lesson').order_by('lesson__order', 'order', 'id')
        targets = [row for row in queryset if has_missing_correct(row)]
        self.stdout.write(f'Aniqlandi: {len(targets)} ta correct=null topshiriq.')
        if not targets:
            if options['dry_run']:
                return
            with transaction.atomic():
                marked = sum(mark_first_example(row) for row in queryset)
            self.stdout.write(self.style.SUCCESS(f'{marked} ta topshiriqqa namuna belgisi qo‘shildi.'))
            return
        if len(targets) != 32:
            self.stdout.write(self.style.WARNING(
                f'Kutilgan son 32, amaldagi son {len(targets)}. Faqat aniqlanganlar ishlanadi.'
            ))

        corrupt = [
            row for row in targets
            if row.lesson.order == 22 and row.order in CORRUPT_UNIT_22_ORDERS
        ]
        targets = [row for row in targets if row not in corrupt]
        if options['dry_run']:
            self.stdout.write(f'[DRY] {len(corrupt)} dublikat o‘chiriladi, {len(targets)} ta’mirlanadi.')
            return

        api_key = env('GEMINI_API_KRY', default=None) or env('GEMINI_API_KEY', default=None)
        if not api_key:
            raise CommandError('GEMINI_API_KEY yoki GEMINI_API_KRY topilmadi.')
        model_name = env('GEMINI_MODEL', default='gemini-2.5-flash')

        prepared = []
        for exercise in targets:
            content = special_case_content(exercise)
            exercise.content = content
            override = MISSING_AUDIO.get((exercise.lesson.order, exercise.instruction))
            if override:
                exercise.audio_url = override
            questions = content.get('questions') or content.get('sentences') or []
            audio_urls = sibling_audio_urls(exercise.audio_url, len(questions))
            prepared.append((exercise, questions, audio_urls))

        def solve(item):
            exercise, questions, audio_urls = item
            client = genai.Client(api_key=api_key)
            clean_rows = [
                {'question': row.get('question', ''), 'options': row.get('options', [])}
                for row in questions
            ]
            prompt = (
                'Solve this English listening exercise accurately. Return one zero-based '
                'correct option index for every row, in the same order. If several numbered '
                'audio clips are attached, clip N belongs to row N. If one combined clip is '
                'attached, it contains the answers in row order. Use the page image for visual '
                'context when supplied. Return JSON only as '
                '{"correct_indices":[0,1,...]}.\n\nRows:\n'
                + json.dumps(clean_rows, ensure_ascii=False)
            )
            contents = [prompt]
            image_path = local_path((exercise.content or {}).get('image_url'))
            if image_path:
                contents.extend([
                    'Source page image:',
                    types.Part.from_bytes(data=image_path.read_bytes(), mime_type='image/jpeg'),
                ])
            for index, url in enumerate(audio_urls, start=1):
                path = local_path(url)
                if path:
                    label = f'Audio clip for row {index}:' if len(audio_urls) > 1 else 'Combined audio:'
                    contents.extend([
                        label,
                        types.Part.from_bytes(data=path.read_bytes(), mime_type='audio/mpeg'),
                    ])
            if not any(isinstance(part, types.Part) and part.inline_data for part in contents):
                raise ValueError('Audio yoki source image topilmadi')

            last_error = None
            for attempt in range(1, 4):
                try:
                    response = client.models.generate_content(
                        model=model_name,
                        contents=contents,
                        config=types.GenerateContentConfig(
                            temperature=0,
                            response_mime_type='application/json',
                        ),
                    )
                    data = json.loads(response.text)
                    indices = data.get('correct_indices') or []
                    if len(indices) != len(questions):
                        raise ValueError(f'{len(questions)} o‘rniga {len(indices)} indeks qaytdi')
                    normalized = [int(value) for value in indices]
                    for row, value in zip(questions, normalized):
                        if value < 0 or value >= len(row.get('options') or []):
                            raise ValueError(f'Noto‘g‘ri indeks: {value}')
                    return exercise.id, normalized, audio_urls
                except Exception as error:
                    last_error = error
                    time.sleep(10 * attempt)
            raise RuntimeError(f'Exercise {exercise.id}: {last_error}')

        solved = {}
        failures = []
        workers = max(1, min(options['workers'], 6))
        with ThreadPoolExecutor(max_workers=workers) as executor:
            future_map = {executor.submit(solve, item): item[0] for item in prepared}
            for future in as_completed(future_map):
                exercise = future_map[future]
                try:
                    exercise_id, indices, audio_urls = future.result()
                    solved[exercise_id] = (indices, audio_urls)
                    self.stdout.write(f'  ✔ U{exercise.lesson.order:02d} / #{exercise.id}: {indices}')
                except Exception as error:
                    failures.append((exercise.id, str(error)))
                    self.stderr.write(f'  ✗ #{exercise.id}: {error}')
                if options['delay'] > 0:
                    time.sleep(options['delay'])

        if failures:
            raise CommandError(f'{len(failures)} ta topshiriq yechilmadi; baza o‘zgartirilmadi.')

        with transaction.atomic():
            deleted, _ = Exercise.objects.filter(id__in=[row.id for row in corrupt]).delete()
            for exercise, questions, audio_urls in prepared:
                indices, audio_urls = solved[exercise.id]
                content = dict(exercise.content or {})
                key = 'questions' if content.get('questions') is not None else 'sentences'
                content[key] = [
                    {
                        **row,
                        'correct': indices[index],
                        **({'is_example': True} if index == 0 and len(questions) >= 2 else {}),
                    }
                    for index, row in enumerate(questions)
                ]
                if len(audio_urls) > 1:
                    content['audio_urls'] = audio_urls
                exercise.content = content
                exercise.has_audio = bool(exercise.audio_url)
                exercise.save(update_fields=['content', 'audio_url', 'has_audio'])
            marked = sum(mark_first_example(row) for row in Exercise.objects.filter(
                lesson__title__startswith='[Book 1]'
            ))

        self.stdout.write(self.style.SUCCESS(
            f'Tayyor: {len(solved)} topshiriq tuzatildi, {deleted} yaroqsiz dublikat o‘chirildi, '
            f'{marked} ta namuna belgilandi.'
        ))
