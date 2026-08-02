"""Attach verified Practice Book pages to the existing reading exercises.

The mapping was audited against the 176 local page images. The command is
idempotent and intentionally matches by unit + reading order instead of DB ids.
"""
from django.core.management.base import BaseCommand
from django.db import transaction
from django.db.models import Max

from courses.models import Lesson
from quiz.models import Exercise


BOOK_PAGE_URL = (
    '/static/book/'
    'English_for_Everyone_-_Level_1_Beginner_-_Practice_Book_page-{page:04d}.jpg'
)

# (current unit, verified unit, page number, zero-based reading occurrence)
# Unit 06's page was historically imported into Unit 12; the command repairs it.
READING_SOURCES = [
    (12, 6, 23, 0),
    (14, 14, 44, 0),
    (15, 15, 47, 0),
    (15, 15, 48, 1),
    (17, 17, 57, 0),
    (19, 19, 63, 0),
    (21, 21, 69, 0),
    (28, 28, 89, 0),
    (35, 35, 112, 0),
    (39, 39, 124, 0),
    (40, 40, 130, 0),
    (40, 40, 131, 1),
    (42, 42, 136, 0),
]

# Pages whose reading task was skipped by the original AI importer. Answers were
# manually verified against the original page and its passage.
MISSING_READING_EXERCISES = [
    {
        'unit': 8, 'page': 29,
        'instruction': 'Read the email and sort the determiners and pronouns',
        'passage_title': 'A new pet',
        'sentences': [
            {'text': 'Thank you for ___ email.', 'answer': 'your', 'is_example': True},
            {'text': '___ name is Rex.', 'answer': 'His'},
            {'text': 'I take him for a walk with ___ girlfriend Jane.', 'answer': 'my'},
            {'text': "Jane's dog is small, but ___ is very small.", 'answer': 'hers'},
            {'text': "Jane's dog likes ___!", 'answer': 'mine'},
            {'text': 'We go to the park with ___ dogs every day.', 'answer': 'our'},
        ],
    },
    {
        'unit': 16, 'page': 53,
        'instruction': 'Read the article and answer the questions',
        'passage_title': 'What I do',
        'questions': [
            {'question': "Who doesn't live in a city?", 'options': ['Sam', 'Carla', 'Greg'], 'correct': 2, 'is_example': True},
            {'question': 'Who plays a sport on Thursdays?', 'options': ['Sam', 'Carla', 'Greg'], 'correct': 1},
            {'question': 'Who works in the evenings?', 'options': ['Sam', 'Carla', 'Greg'], 'correct': 0},
            {'question': "Who doesn't have lunch?", 'options': ['Sam', 'Carla', 'Greg'], 'correct': 2},
            {'question': 'Who works in an office?', 'options': ['Sam', 'Carla', 'Greg'], 'correct': 1},
            {'question': "Who doesn't work on Mondays?", 'options': ['Sam', 'Carla', 'Greg'], 'correct': 0},
            {'question': 'Who starts work at 5am?', 'options': ['Sam', 'Carla', 'Greg'], 'correct': 2},
            {'question': 'Who plays basketball on Mondays?', 'options': ['Sam', 'Carla', 'Greg'], 'correct': 0},
            {'question': 'Who plays soccer?', 'options': ['Sam', 'Carla', 'Greg'], 'correct': 1},
        ],
    },
    {
        'unit': 18, 'page': 59,
        'instruction': 'Read the email and write full-sentence answers',
        'passage_title': 'My new job',
        'sentences': [
            {'text': 'Does Helen have a new job? ___', 'answer': 'Yes, she does.', 'is_example': True},
            {'text': 'Is Helen a German teacher? ___', 'answer': "No, she isn't."},
            {'text': 'Does Helen start work at 8am? ___', 'answer': "No, she doesn't."},
            {'text': "Is Helen's school small? ___", 'answer': "No, it isn't."},
            {'text': 'Does Helen finish at 4pm? ___', 'answer': 'Yes, she does.'},
            {'text': 'Does Helen read a book in the evening? ___', 'answer': "No, she doesn't."},
        ],
    },
    {
        'unit': 22, 'page': 71,
        'instruction': 'Read the postcard and fill in a, an, some, or the',
        'passage_title': 'Postcard from Glennmuir',
        'sentences': [
            {'text': 'We are in Glennmuir, ___ quiet town in Scotland.', 'answer': 'a', 'is_example': True},
            {'text': "There's ___ castle here.", 'answer': 'a'},
            {'text': "There's ___ cathedral here.", 'answer': 'a'},
            {'text': "They're beautiful and ___ castle is really old.", 'answer': 'the'},
            {'text': 'There are ___ interesting stores.', 'answer': 'some'},
            {'text': 'We also have ___ new friend here.', 'answer': 'a'},
            {'text': 'He works as ___ waiter.', 'answer': 'a'},
            {'text': 'He works in ___ Italian restaurant.', 'answer': 'an'},
            {'text': 'The restaurant is next to ___ shopping mall.', 'answer': 'the'},
        ],
    },
    {
        'unit': 25, 'page': 81,
        'instruction': 'Read the email and find eight adjectives',
        'passage_title': 'Introducing myself',
        'sentences': [
            {'text': 'The town is really ___.', 'answer': 'small', 'is_example': True},
            {'text': "There aren't any ___ cafés or bars.", 'answer': 'good'},
            {'text': 'The town is really ___.', 'answer': 'beautiful'},
            {'text': "There's a ___ park.", 'answer': 'wonderful'},
            {'text': 'The park is very ___.', 'answer': 'busy'},
            {'text': 'Foxby has ___ buildings.', 'answer': 'interesting'},
            {'text': "There's an ___ church.", 'answer': 'old'},
            {'text': "There's a ___ castle.", 'answer': 'large'},
        ],
    },
]

READING_TERMS = ('read ', 'read the', 'advertisement')


def _reading_candidates(unit):
    rows = Exercise.objects.filter(lesson__order=unit).select_related('lesson').order_by('order', 'id')
    return [
        row for row in rows
        if any(term in row.instruction.lower() for term in READING_TERMS)
    ]


def _as_reading_content(exercise, page):
    old = dict(exercise.content or {})
    content = {**old, 'pages': [{
        'url': BOOK_PAGE_URL.format(page=page),
        'page_number': page,
        'caption': f'Practice Book — {page}-sahifa',
    }]}

    if 'questions' not in content and old.get('sentences'):
        sentences = old['sentences']
        if all(isinstance(item, dict) and item.get('options') for item in sentences):
            content.pop('sentences', None)
            content['questions'] = [
                {
                    'question': f"{item.get('before', '')}{item.get('after', '')}".strip(),
                    'options': item.get('options', []),
                    'correct': item.get('correct', item.get('correct_index', 0)),
                    **({'is_example': True} if index == 0 else {}),
                }
                for index, item in enumerate(sentences)
            ]
        elif sentences:
            content['sentences'] = [
                {**item, **({'is_example': True} if index == 0 else {})}
                for index, item in enumerate(sentences)
            ]
    elif content.get('questions'):
        content['questions'] = [
            {**item, **({'is_example': True} if index == 0 else {})}
            for index, item in enumerate(content['questions'])
        ]
    return content


class Command(BaseCommand):
    help = "Mavjud reading mashqlarini tekshirilgan kitob sahifalariga bog'laydi"

    def add_arguments(self, parser):
        parser.add_argument('--dry-run', action='store_true')

    @transaction.atomic
    def handle(self, *args, **options):
        dry_run = options['dry_run']
        changed = 0
        skipped = 0

        for current_unit, verified_unit, page, occurrence in READING_SOURCES:
            page_url = BOOK_PAGE_URL.format(page=page)
            exercise = next((
                row for row in Exercise.objects.filter(type='reading').select_related('lesson')
                if any(
                    (item == page_url) if isinstance(item, str) else item.get('url') == page_url
                    for item in (row.content or {}).get('pages', [])
                )
            ), None)
            if exercise is None:
                candidates = _reading_candidates(current_unit)
                if occurrence >= len(candidates):
                    self.stdout.write(self.style.WARNING(
                        f'Unit {current_unit:02d}, reading #{occurrence + 1}: topilmadi'
                    ))
                    skipped += 1
                    continue
                exercise = candidates[occurrence]
            target_lesson = Lesson.objects.filter(order=verified_unit, title__startswith='[Book 1]').first()
            if not target_lesson:
                self.stdout.write(self.style.WARNING(f'Unit {verified_unit:02d}: dars topilmadi'))
                skipped += 1
                continue

            exercise.lesson = target_lesson
            exercise.type = 'reading'
            exercise.content = _as_reading_content(exercise, page)
            exercise.has_audio = False
            exercise.audio_url = None
            if not dry_run:
                exercise.save(update_fields=['lesson', 'type', 'content', 'has_audio', 'audio_url'])
            changed += 1
            self.stdout.write(
                f"{'[DRY] ' if dry_run else ''}Unit {verified_unit:02d}: "
                f'{page}-sahifa → {exercise.instruction[:55]}'
            )

        for definition in MISSING_READING_EXERCISES:
            unit = definition['unit']
            page = definition['page']
            page_url = BOOK_PAGE_URL.format(page=page)
            target_lesson = Lesson.objects.filter(order=unit, title__startswith='[Book 1]').first()
            if not target_lesson:
                self.stdout.write(self.style.WARNING(f'Unit {unit:02d}: dars topilmadi'))
                skipped += 1
                continue

            existing = next((
                row for row in Exercise.objects.filter(type='reading', lesson=target_lesson)
                if any(
                    (item == page_url) if isinstance(item, str) else item.get('url') == page_url
                    for item in (row.content or {}).get('pages', [])
                )
            ), None)
            was_existing = existing is not None
            content = {
                'passage_title': definition['passage_title'],
                'pages': [{
                    'url': page_url,
                    'page_number': page,
                    'caption': f'Practice Book — {page}-sahifa',
                }],
            }
            if 'questions' in definition:
                content['questions'] = definition['questions']
            else:
                content['sentences'] = definition['sentences']

            if not dry_run:
                if existing:
                    existing.instruction = definition['instruction']
                    existing.content = content
                    existing.save(update_fields=['instruction', 'content'])
                else:
                    next_order = (Exercise.objects.filter(lesson=target_lesson).aggregate(value=Max('order'))['value'] or 0) + 1
                    existing = Exercise.objects.create(
                        lesson=target_lesson,
                        type='reading',
                        instruction=definition['instruction'],
                        content=content,
                        order=next_order,
                    )
            changed += 1
            self.stdout.write(
                f"{'[DRY] ' if dry_run else ''}Unit {unit:02d}: {page}-sahifa → "
                f"{definition['instruction']} {'(yangilandi)' if was_existing else '(yangi)'}"
            )

        if dry_run:
            transaction.set_rollback(True)
        self.stdout.write(self.style.SUCCESS(
            f'Tayyor: {changed} ta reading bog\'landi, {skipped} ta topilmadi.'
        ))
