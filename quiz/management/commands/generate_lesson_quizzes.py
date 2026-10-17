"""Generate a five-question end-of-lesson quiz from verified exercises."""
import hashlib
import re

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction


QUIZZES_PER_LESSON = 5
PLACEHOLDER_QUESTION_RE = re.compile(
    r'^(?:complete the sentence:\s*)?_+$',
    flags=re.IGNORECASE,
)

# Two short visual/reading sections expose fewer than five reusable rows.
# These questions are derived directly from their imported page content.
LESSON_FALLBACKS = {
    '[Book 2] Unit 14': [
        {
            'question': 'Which word means the bags and suitcases you take on a journey?',
            'options': ['luggage', 'reception', 'security', 'hostel'],
            'correct_option_index': 0,
        },
    ],
    '[Book 2] Unit 48': [
        {
            'question': "Which entrée on Adam's Kitchen menu costs $7.95?",
            'options': ['Onion and bean tart', 'Beef and ale pie', 'Spicy pasta'],
            'correct_option_index': 0,
        },
        {
            'question': 'Which dessert is served with vanilla ice cream?',
            'options': ['Lemon cheesecake', 'Chocolate pudding', 'Strawberry cake'],
            'correct_option_index': 2,
        },
    ],
}


def clean_text(value):
    return re.sub(r'\s+', ' ', str(value or '')).strip()


def unique_strings(values):
    result = []
    seen = set()
    for value in values:
        text = clean_text(value)
        key = text.casefold()
        if text and key not in seen:
            result.append(text)
            seen.add(key)
    return result


def answer_text(value):
    if isinstance(value, list):
        return ' / '.join(clean_text(item) for item in value)
    return clean_text(value)


def rotate_options(question, correct, distractors, limit=4):
    """Create stable option order without putting every answer at index zero."""
    options = unique_strings([correct, *distractors])[:limit]
    if len(options) < 2:
        return None
    correct_text = clean_text(correct)
    offset = int(hashlib.sha256(question.encode('utf-8')).hexdigest()[:8], 16) % len(options)
    options = options[offset:] + options[:offset]
    return options, options.index(correct_text)


def multiple_choice_candidate(row):
    options = unique_strings(row.get('options') or [])
    correct = row.get('correct', row.get('correct_index'))
    if not isinstance(correct, int) or len(options) < 2 or not 0 <= correct < len(options):
        return None
    before = clean_text(row.get('before'))
    after = clean_text(row.get('after'))
    if before or after:
        body = f'{before} ___ {after}'
        question = f'Complete the sentence: {clean_text(body)}'
    else:
        question = clean_text(row.get('question') or row.get('text') or row.get('sentence'))
        if not question:
            question = 'Choose the grammatically correct sentence.'
    if not question:
        return None
    return {
        'question': question,
        'options': options,
        'correct_option_index': correct,
    }


def fill_blank_candidates(content):
    rows = content.get('sentences') or content.get('items') or []
    answer_pool = unique_strings([
        *(content.get('word_panel') or []),
        *(answer_text(row.get('answer')) for row in rows if isinstance(row, dict)),
    ])
    result = []
    seen_questions = set()
    for row in rows:
        if not isinstance(row, dict) or not row.get('answer'):
            continue
        answer = answer_text(row['answer'])
        text = clean_text(row.get('text') or row.get('sentence'))
        if not answer or not text or not re.search(r'[A-Za-z0-9]', text):
            continue
        question = f'Complete the sentence: {text}'
        question_key = question.casefold()
        # Some source-book activities ask learners to write several possible
        # answers for the same sentence. They cannot safely become separate
        # single-answer multiple-choice questions.
        if question_key in seen_questions:
            continue
        distractors = [
            *(row.get('alternatives') or []),
            *(value for value in answer_pool if value.casefold() != answer.casefold()),
        ]
        rotated = rotate_options(question, answer, distractors)
        if not rotated:
            continue
        options, correct = rotated
        seen_questions.add(question_key)
        result.append({
            'question': question,
            'options': options,
            'correct_option_index': correct,
        })
    return result


def written_candidates(content):
    rows = content.get('questions') or []
    answer_pool = unique_strings(answer_text(row.get('answer')) for row in rows if isinstance(row, dict))
    result = []
    for row in rows:
        if not isinstance(row, dict):
            continue
        question = clean_text(row.get('prompt'))
        answer = answer_text(row.get('answer'))
        if not question or not answer:
            continue
        rotated = rotate_options(
            question,
            answer,
            [value for value in answer_pool if value.casefold() != answer.casefold()],
        )
        if rotated:
            options, correct = rotated
            result.append({
                'question': f'Write the correct form: {question}',
                'options': options,
                'correct_option_index': correct,
            })
    return result


def word_order_candidates(content):
    rows = content.get('items') or []
    answer_pool = unique_strings(row.get('answer') for row in rows if isinstance(row, dict))
    result = []
    for row in rows:
        if not isinstance(row, dict):
            continue
        answer = clean_text(row.get('answer'))
        tokens = row.get('tokens') or []
        if not answer or len(tokens) < 2:
            continue
        prompt = ' / '.join(str(token) for token in reversed(tokens))
        question = f'Choose the correctly ordered sentence: {prompt}'
        rotated = rotate_options(
            question,
            answer,
            [value for value in answer_pool if value.casefold() != answer.casefold()],
        )
        if rotated:
            options, correct = rotated
            result.append({
                'question': question,
                'options': options,
                'correct_option_index': correct,
            })
    return result


def matching_candidates(content):
    left = content.get('left') or []
    right = content.get('right') or []
    pairs = content.get('pairs') or []
    right_options = unique_strings(right)
    if len(left) != len(pairs) or len(right_options) < 2:
        return []
    result = []
    for index, left_value in enumerate(left):
        right_index = pairs[index]
        if not isinstance(right_index, int) or not 0 <= right_index < len(right):
            continue
        answer = clean_text(right[right_index])
        question = f'Match this item with the correct answer: {clean_text(left_value)}'
        rotated = rotate_options(
            question,
            answer,
            [value for value in right_options if value.casefold() != answer.casefold()],
        )
        if not rotated:
            continue
        options, correct = rotated
        result.append({
            'question': question,
            'options': options,
            'correct_option_index': correct,
        })
    return result


def candidates_for_exercise(exercise):
    content = exercise.content or {}
    if exercise.type == 'listening':
        return []
    if exercise.type == 'matching':
        return matching_candidates(content)
    if exercise.type == 'written_answer':
        return written_candidates(content)
    if exercise.type == 'word_order':
        return word_order_candidates(content)
    if exercise.type == 'fill_blank' or (
        exercise.type == 'reading' and content.get('sentences')
    ):
        return fill_blank_candidates(content)
    rows = content.get('questions') or content.get('sentences') or content.get('items') or []
    return [candidate for row in rows if isinstance(row, dict)
            if (candidate := multiple_choice_candidate(row))]


def lesson_candidates(lesson):
    priority = {
        'choose_correct': 0,
        'fill_blank': 1,
        'matching': 2,
        'reading': 3,
        'listening': 4,
    }
    exercises = sorted(
        lesson.exercises.all(),
        key=lambda row: (priority.get(row.type, 9), row.order, row.id),
    )
    groups = [candidates_for_exercise(exercise) for exercise in exercises]
    groups = [group for group in groups if group]

    # Round-robin keeps the final test representative of the whole lesson.
    ordered = []
    for row_index in range(max((len(group) for group in groups), default=0)):
        for group in groups:
            if row_index < len(group):
                ordered.append(group[row_index])
    for prefix, fallback in LESSON_FALLBACKS.items():
        if lesson.title.startswith(prefix):
            ordered.extend(fallback)

    result = []
    fingerprints = set()
    for row in ordered:
        options = unique_strings(row.get('options') or [])
        correct = row.get('correct_option_index')
        question = clean_text(row.get('question'))
        if not question or len(options) < 2 or not isinstance(correct, int) or not 0 <= correct < len(options):
            continue
        fingerprint = (
            question.casefold(),
            tuple(sorted(option.casefold() for option in options)),
        )
        if fingerprint in fingerprints:
            continue
        fingerprints.add(fingerprint)
        result.append({
            'question': question,
            'options': options,
            'correct_option_index': correct,
        })
    return result


class Command(BaseCommand):
    help = 'Har bir darsga mavjud mashqlardan 5 tadan yakuniy test yaratadi'

    def add_arguments(self, parser):
        parser.add_argument('--per-lesson', type=int, default=QUIZZES_PER_LESSON)
        parser.add_argument('--dry-run', action='store_true')
        parser.add_argument('--replace', action='store_true')

    def handle(self, *args, **options):
        from courses.models import Lesson
        from quiz.models import Quiz

        desired = options['per_lesson']
        if desired < 2 or desired > 20:
            raise CommandError('--per-lesson 2–20 oralig‘ida bo‘lishi kerak.')

        lessons = list(Lesson.objects.prefetch_related('exercises', 'quizzes').order_by('id'))
        plan = []
        repairs = []
        failures = []
        for lesson in lessons:
            existing = [] if options['replace'] else list(lesson.quizzes.all())
            for quiz in existing:
                if PLACEHOLDER_QUESTION_RE.fullmatch(clean_text(quiz.question)):
                    quiz.question = 'Choose the grammatically correct sentence.'
                    repairs.append(quiz)
            needed = max(0, desired - len(existing))
            if not needed:
                continue
            existing_questions = {clean_text(row.question).casefold() for row in existing}
            candidates = [
                row for row in lesson_candidates(lesson)
                if clean_text(row['question']).casefold() not in existing_questions
            ]
            if len(candidates) < needed:
                failures.append(
                    f'{lesson.id} / {lesson.title}: {needed} kerak, {len(candidates)} topildi'
                )
                continue
            plan.append((lesson, candidates[:needed]))

        if failures:
            raise CommandError('Test yetishmaydigan darslar:\n' + '\n'.join(failures))

        new_count = sum(len(rows) for _, rows in plan)
        self.stdout.write(
            f'Reja: {len(lessons)} darsdan {len(plan)} tasiga {new_count} ta test; '
            f'{len(repairs)} ta placeholder savol tuzatiladi.'
        )
        if options['dry_run']:
            return

        with transaction.atomic():
            if options['replace']:
                Quiz.objects.all().delete()
            if repairs:
                Quiz.objects.bulk_update(repairs, ['question'])
            for lesson, rows in plan:
                Quiz.objects.bulk_create([
                    Quiz(lesson=lesson, **row) for row in rows
                ])

        total = Quiz.objects.count()
        without = Lesson.objects.filter(quizzes__isnull=True).count()
        self.stdout.write(self.style.SUCCESS(
            f'Tayyor: {new_count} yangi test. Jami {total}; testsiz darslar {without}.'
        ))
