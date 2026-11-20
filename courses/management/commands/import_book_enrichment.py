"""Import reviewed, offline book manifests without replacing existing lessons."""
import hashlib
import json
import re
from collections import Counter
from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.db.models import Max

from courses.models import Lesson, Vocabulary
from quiz.models import Exercise
from quiz.serializers import ExerciseSerializer
from quiz.views import _grade_exercise


SOURCE = 'book_enrichment_v2'


def normalized(value):
    return re.sub(r'\s+', ' ', str(value or '').replace('’', "'").replace('‘', "'")).strip().casefold()


def fingerprint(content, audio_url=None):
    keys = ['questions', 'sentences', 'items', 'left', 'right', 'pairs']
    core = {key: content[key] for key in keys if key in content}
    resources = {key: content[key] for key in ['audio_urls', 'pages', 'image_url', 'images', 'passage'] if content.get(key)}
    if audio_url:
        resources['audio_url'] = audio_url
    if resources:
        core['resource_context'] = resources
    if 'example_count' in content:
        core['example_count'] = content['example_count']
    return hashlib.sha256(normalized(json.dumps(core, sort_keys=True, ensure_ascii=False)).encode()).hexdigest()


def asset_urls(value):
    if isinstance(value, str):
        if value.startswith(('/static/', '/media/')):
            yield value
    elif isinstance(value, dict):
        for item in value.values():
            yield from asset_urls(item)
    elif isinstance(value, list):
        for item in value:
            yield from asset_urls(item)


def perfect_answer(exercise):
    content = exercise.content
    rows = content.get('questions') or content.get('sentences') or content.get('items') or []
    start = content.get('example_count', 1 if len(rows) >= 2 else 0)
    scored = rows[start:]
    if exercise.type == 'matching' or (exercise.type == 'listening' and content.get('left')):
        return {'matches': {str(index): value for index, value in enumerate(content['pairs'])}}
    if exercise.type in {'fill_blank', 'written_answer', 'word_order'} or (
        exercise.type in {'reading', 'listening'} and content.get('sentences')
    ):
        return {'answers': [row['answer'] for row in scored]}
    choices = [row.get('correct_indices', row.get('correct', row.get('correct_index', 0))) for row in scored]
    return {'answers': choices if exercise.type == 'choose_correct' else {str(index): value for index, value in enumerate(choices)}}


class Command(BaseCommand):
    help = 'Add reviewed Level 1/2 content, preserving existing IDs, tests, attempts, and group settings.'

    def add_arguments(self, parser):
        parser.add_argument('--manifest', action='append', help='Reviewed JSON file; repeat for multiple files.')
        parser.add_argument('--dry-run', action='store_true')
        parser.add_argument('--skip-asset-check', action='store_true', help='Only allowed for a staging dry run.')

    @transaction.atomic
    def handle(self, *args, **options):
        if options['skip_asset_check'] and not options['dry_run']:
            raise CommandError('Asset checks can only be skipped during a dry run.')
        paths = options['manifest'] or [
            str(Path(settings.BASE_DIR) / 'courses/data/book_enrichment_v2/level1.json'),
            str(Path(settings.BASE_DIR) / 'courses/data/book_enrichment_v2/level2.json'),
        ]
        totals = Counter()
        known_keys = set()
        for path in paths:
            try:
                manifest = json.loads(Path(path).read_text(encoding='utf-8'))
            except (OSError, ValueError) as error:
                raise CommandError(f'Manifest cannot be read: {path}: {error}') from error
            level = manifest.get('level')
            if level not in {1, 2} or not isinstance(manifest.get('lessons'), list):
                raise CommandError(f'Invalid book manifest: {path}')
            if manifest.get('review_status') != 'reviewed':
                raise CommandError(f'Manifest has not finished review: {path}')
            level_totals = Counter()
            for definition in manifest['lessons']:
                self.import_lesson(definition, level, level_totals, known_keys, options)
            totals.update(level_totals)
            self.stdout.write(json.dumps({'level': level, **dict(level_totals)}, ensure_ascii=False, sort_keys=True))
        if options['dry_run']:
            transaction.set_rollback(True)
        self.stdout.write(self.style.SUCCESS(json.dumps(
            {'dry_run': options['dry_run'], **dict(totals)}, ensure_ascii=False, sort_keys=True,
        )))

    def import_lesson(self, definition, level, counts, known_keys, options):
        try:
            lesson = Lesson.objects.select_related('category').get(pk=definition['lesson_id'])
        except (Lesson.DoesNotExist, KeyError) as error:
            raise CommandError(f'Target lesson not found: {definition.get("lesson_id")}') from error
        expected_category = 'Book 1 – Beginner' if level == 1 else 'Book 2 – Elementary'
        if not lesson.category or lesson.category.name != expected_category:
            raise CommandError(f'Lesson {lesson.id} is not in {expected_category}')
        counts['lessons_reviewed'] += 1

        changed = []
        for field in ['description_kaa', 'description_uz']:
            text = str(definition.get(field) or '').strip()
            if not text:
                raise CommandError(f'Missing bilingual theory: {lesson.id}/{field}')
            current = getattr(lesson, field) or ''
            if normalized(current) == normalized(text):
                continue
            if len(current.strip()) >= 150:
                counts['existing_theory_preserved'] += 1
                continue
            setattr(lesson, field, text)
            changed.append(field)
        if changed:
            lesson.save(update_fields=changed)
            counts['theory_lessons_updated'] += 1

        vocab_keys = {
            (normalized(row.word), normalized(row.translation_uz or row.translation))
            for row in lesson.vocabulary.all()
        }
        vocab_order = lesson.vocabulary.aggregate(value=Max('order'))['value'] or 0
        for row in definition.get('vocabulary', []):
            if any(not str(row.get(field) or '').strip() for field in ['word', 'translation_kaa', 'translation_uz']):
                raise CommandError(f'Incomplete bilingual vocabulary in lesson {lesson.id}: {row}')
            marker = (normalized(row['word']), normalized(row['translation_uz']))
            key = f'l{level}.lesson{lesson.id}.word.' + hashlib.sha256('|'.join(marker).encode()).hexdigest()[:20]
            if marker in vocab_keys or Vocabulary.objects.filter(source=SOURCE, source_key=key).exists():
                counts['vocabulary_skipped_existing'] += 1
                continue
            vocab_order += 1
            Vocabulary.objects.create(
                lesson=lesson, word=row['word'].strip(), translation=row['translation_kaa'].strip(),
                translation_kaa=row['translation_kaa'].strip(), translation_uz=row['translation_uz'].strip(),
                example=str(row.get('example') or '').strip(), order=vocab_order,
                source=SOURCE, source_key=key,
                source_unit=row.get('source_unit', definition.get('source_unit')),
            )
            vocab_keys.add(marker)
            counts['vocabulary_created'] += 1

        existing = {(row.type, fingerprint(row.content, row.audio_url)) for row in lesson.exercises.all()}
        exercise_order = lesson.exercises.aggregate(value=Max('order'))['value'] or 0
        for row in definition.get('exercises', []):
            key = row.get('source_key')
            if not isinstance(key, str) or not key.startswith(f'l{level}.') or len(key) > 160:
                raise CommandError(f'Invalid source key in lesson {lesson.id}: {key}')
            if key in known_keys:
                raise CommandError(f'Duplicate activity source key in manifests: {key}')
            known_keys.add(key)
            if Exercise.objects.filter(source=SOURCE, source_key=key).exists():
                counts['exercises_skipped_existing'] += 1
                continue
            content = row.get('content') or {}
            provenance = content.get('provenance') or {}
            if (
                provenance.get('level') != level or provenance.get('book') not in {'course', 'practice'}
                or not provenance.get('pages') or not provenance.get('activity')
            ):
                raise CommandError(f'Missing book/page/activity provenance: {key}')
            max_unit = 48 if level == 1 else 49
            max_page = 184 if provenance['book'] == 'course' else 176
            if type(provenance.get('unit')) is not int or not 1 <= provenance['unit'] <= max_unit:
                raise CommandError(f'Invalid original book unit: {key}')
            for page in [*provenance['pages'], *provenance.get('answer_pages', [])]:
                if type(page) is not int or not 1 <= page <= max_page:
                    raise CommandError(f'Invalid source page for {key}: {page}')
            marker = (row.get('type'), fingerprint(content, row.get('audio_url')))
            if marker in existing:
                counts['exercises_skipped_duplicate'] += 1
                continue
            if not options['skip_asset_check']:
                base = Path(settings.BASE_DIR).resolve()
                for url in asset_urls([row.get('audio_url'), content]):
                    target = (base / url.lstrip('/')).resolve()
                    if not target.is_relative_to(base) or not target.is_file():
                        raise CommandError(f'Missing asset for {key}: {url}')
            exercise_order += 1
            payload = {
                'lesson': lesson.id, 'type': row.get('type'), 'content': content,
                'instruction': row.get('instruction_kaa', ''),
                'instruction_kaa': row.get('instruction_kaa', ''),
                'instruction_uz': row.get('instruction_uz', ''),
                'source': SOURCE, 'source_unit': row.get('source_unit', definition.get('source_unit')),
                'order': exercise_order, 'audio_url': row.get('audio_url'),
                'has_audio': bool(row.get('audio_url') or any(content.get('audio_urls') or [])),
            }
            if not payload['instruction_kaa'] or not payload['instruction_uz']:
                raise CommandError(f'Missing bilingual instruction: {key}')
            serializer = ExerciseSerializer(data=payload)
            if not serializer.is_valid():
                raise CommandError(f'Invalid {key}: {serializer.errors}')
            candidate = Exercise(lesson=lesson, type=payload['type'], content=content)
            if _grade_exercise(candidate, perfect_answer(candidate)) != (True, 100):
                raise CommandError(f'Correct-answer grading failed for {key}')
            serializer.save(source_key=key)
            existing.add(marker)
            counts['exercises_created'] += 1
            counts[f'type_{payload["type"]}'] += 1
