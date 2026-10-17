import copy
import json
import re
from collections import Counter
from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.db.models import Max

from courses.models import Lesson
from quiz.models import Exercise, Quiz


SUPPLEMENT_SOURCE = 'course_book_supplement_v1'


def rows_for(content):
    for key in ('sentences', 'questions', 'items'):
        if isinstance(content.get(key), list):
            return key, content[key]
    return None, []


def deduplicate_options(row):
    options = row.get('options')
    correct_key = 'correct' if 'correct' in row else 'correct_index'
    correct = row.get(correct_key)
    if not isinstance(options, list) or not isinstance(correct, int) or not 0 <= correct < len(options):
        return False
    correct_value = options[correct]
    unique = []
    seen = set()
    for option in options:
        marker = str(option).strip().casefold()
        if marker not in seen:
            seen.add(marker)
            unique.append(option)
    if unique == options:
        return False
    row['options'] = unique
    row[correct_key] = next(
        index for index, option in enumerate(unique)
        if str(option).strip().casefold() == str(correct_value).strip().casefold()
    )
    return True


def split_second_conditional(answer):
    words = answer.split()
    if 'would' not in words:
        return None
    position = words.index('would')
    if position == 1:
        return [words[0], ' '.join(words[1:])]
    if position == 0 and len(words) >= 3:
        return [' '.join(words[:2]), ' '.join(words[2:])]
    return None


def normalize_multi_blank_row(row, instruction):
    text = str(row.get('text') or row.get('sentence') or '')
    answer = row.get('answer')
    blanks = text.count('___')
    if not blanks or isinstance(answer, list):
        return False

    if row.get('answer2'):
        row['answer'] = [answer, row.pop('answer2')]
        return True
    if blanks == 1:
        return False

    if blanks == 2 and '___ a ___' in text and isinstance(answer, str) and ' a ' in answer:
        row['text'] = text.replace('___ a ___', '___')
        return True

    # Two adjacent placeholders were imported for a single phrase such as
    # “am an”. One input is the faithful representation of the source answer.
    collapsed = re.sub(r'___\s+___', '___', text)
    if collapsed != text:
        row['text'] = collapsed
        return True

    if not isinstance(answer, str):
        return False
    parts = [part.strip() for part in re.split(r'\s*(?:,|/)\s*', answer) if part.strip()]
    if len(parts) == blanks:
        row['answer'] = parts
        return True
    if 'second conditional' in instruction.casefold():
        parts = split_second_conditional(answer)
        if parts and len(parts) == blanks:
            row['answer'] = parts
            return True
    return False


MISSING_ANSWER_ROWS = {
    'Say the sentences out loud, filling in the gaps.': [
        ['from', 'to'], 'on', 'on', 'on', ['from', 'to'], 'on', 'on',
        'on', 'on', 'on', ['from', 'to'], 'on', 'on',
    ],
    'SAY THE SENTENCES OUT LOUD, FILLING IN THE GAPS': [
        ['The', 'is', 'and the', 'is'],
        ['The', 'is', 'and the', 'are'],
        ['The', 'is', 'and the', 'are'],
        ['The', 'is', 'and the', 'is'],
        ['The', 'is', 'and the', 'are'],
        ['The', 'is', 'and the', 'are'],
    ],
    'FILL IN THE GAPS USING THE WORDS IN THE PANEL': [
        'There are some', 'There are some', 'There are lots of',
        'There are a few', 'There are a few', 'There are some', 'There are a few',
    ],
}


LISTENING_MATCH_REPAIRS = {
    'Audionı tıńlań hám sáykeslestiń juplar': {
        'pairs': [3, 1, 5, 0, 6, 2, 4, 7],
        'audio_url': '/static/audio/6/6_2.mp3',
    },
    'LISTEN AND MATCH THE PEOPLE TO THEIR POSSESSIONS': {
        'pairs': [1, 0, 4, 5, 2, 3],
        'audio_url': '/static/audio/29/29_3__eg.mp3',
        'audio_urls': [
            '/static/audio/29/29_3__eg.mp3',
            *[f'/static/audio/29/29_3_{index}.mp3' for index in range(1, 6)],
        ],
    },
    'LISTEN TO THE AUDIO AND MATCH THE OBJECTS WITH THEIR OWNERS': {
        'right': ['Our town', 'Adam and I', 'Sally and Jonathan', 'My friend Sam', 'Our house'],
        'pairs': [0, 1, 2, 3, 4],
        'audio_url': '/static/audio/28/28_7_1.mp3',
        'audio_urls': [f'/static/audio/28/28_7_{index}.mp3' for index in range(1, 6)],
        'example_count': 0,
    },
    'Listen to the audio and match the pictures to the names.': {
        'right': ['Sarah', 'Eddie', 'Robert', 'Oliver'],
        'pairs': [0, 1, 2, 3],
        'audio_url': '/static/audio/48/48_8.mp3',
        'example_count': 0,
    },
}


def written_content(content, rows):
    preserved = {
        key: copy.deepcopy(value)
        for key, value in content.items()
        if key not in {'sentences', 'items', 'questions', 'word_panel'}
    }
    preserved['questions'] = [
        {
            'prompt': row.get('text') or row.get('sentence') or row.get('question'),
            'answer': row.get('answer'),
            'alternatives': row.get('alternatives') or [],
            **({'is_example': True} if row.get('is_example') else {}),
        }
        for row in rows
    ]
    return preserved


def repair_contextless_source_rows(exercise, content):
    """Restore prompts that were visible on book pages but lost during import."""
    if exercise.id == 1691:
        prompts = [
            'She lives in California.',
            "She's a waitress in a restaurant.",
            "She isn't Mexican.",
            "Franco isn't an engineer.",
            'They have a daughter in college.',
        ]
        correct = [0, 1, 0, 0, 1]
        exercise.type = 'reading'
        content = {
            'pages': [{'url': '/static/book/English_for_Everyone_-_Level_1_Beginner_-_Practice_Book_page-0047.jpg', 'page_number': 47}],
            'questions': [
                {'question': prompt, 'options': ['True', 'False'], 'correct': answer}
                for prompt, answer in zip(prompts, correct)
            ],
            'example_count': 0,
        }
        return content, True
    if exercise.id == 1693:
        prompts = [
            'Lucia is not 41 years old.',
            "There isn't a learner from Spain.",
            'Pablo is not a teacher.',
            'Theresa is not a teacher.',
            'Xi is not a chef.',
            'Xi does not live in China.',
        ]
        correct = [0, 0, 1, 0, 0, 1]
        exercise.type = 'reading'
        content = {
            'pages': [{'url': '/static/book/English_for_Everyone_-_Level_1_Beginner_-_Practice_Book_page-0048.jpg', 'page_number': 48}],
            'questions': [
                {'question': prompt, 'options': ['True', 'False'], 'correct': answer}
                for prompt, answer in zip(prompts, correct)
            ],
            'example_count': 0,
        }
        return content, True
    if exercise.id == 1702:
        prompts = [
            'Julie gets up at 7am.',
            "Julie doesn't work on Fridays.",
            'Julie has lunch with her friends.',
            'Julie plays tennis on Wednesday evenings.',
            'Julie gets home at 8pm.',
            "Julie doesn't eat dinner.",
            'Julie watches TV before she goes to bed.',
        ]
        correct = [1, 1, 0, 1, 0, 1, 0]
        exercise.type = 'listening'
        exercise.audio_url = '/static/audio/16/16_6.mp3'
        exercise.has_audio = True
        content = {
            'questions': [
                {'question': prompt, 'options': ['True', 'False'], 'correct': answer}
                for prompt, answer in zip(prompts, correct)
            ],
            'example_count': 0,
        }
        return content, True
    if exercise.id == 1919:
        prompts = [
            "I'll apply",
            "I won't worry",
            'If you were me',
            'Have you thought practicing',
            'If I were you, I think of some questions',
            'If I was you',
            "I'll buy something classic",
            'How about ask Gillian',
        ]
        answers = [
            "I'd apply",
            "I wouldn't worry",
            'If I were you',
            'Have you thought of practicing',
            "I'd think of some questions",
            'If I were you',
            "I'd buy something classic",
            'How about asking Gillian',
        ]
        exercise.type = 'written_answer'
        content = {
            'pages': [{'url': '/static/book3/English_for_Everyone_Level_3_Intermediate_Practice_Book_page-0161.jpg', 'page_number': 161}],
            'questions': [
                {'prompt': prompt, 'answer': answer, **({'is_example': True} if index == 0 else {})}
                for index, (prompt, answer) in enumerate(zip(prompts, answers))
            ],
        }
        return content, True
    return content, False


def row_audio_urls(audio_url, count):
    if not audio_url or not audio_url.startswith('/static/audio/'):
        return []
    relative = audio_url.removeprefix('/static/')
    path = Path(settings.BASE_DIR) / 'static' / relative
    match = re.fullmatch(r'(.+)_1(\.mp3)', path.name, flags=re.IGNORECASE)
    prefix = match.group(1) if match else path.stem
    suffix = match.group(2) if match else path.suffix
    candidates = [path.with_name(f'{prefix}_{index}{suffix}') for index in range(1, count + 1)]
    if not all(candidate.exists() for candidate in candidates):
        return []
    return [f'/static/audio/{candidate.relative_to(Path(settings.BASE_DIR) / "static" / "audio").as_posix()}' for candidate in candidates]


def repair_to_be_lesson(lesson):
    exercises = list(lesson.exercises.filter(source=SUPPLEMENT_SOURCE).order_by('order', 'id'))
    if len(exercises) != 2:
        return 0
    choose = next((row for row in exercises if row.type == 'choose_correct'), None)
    matching = next((row for row in exercises if row.type == 'matching'), None)
    if not choose or not matching:
        return 0
    choose.content = {'sentences': [
        {'before': before, 'options': options, 'after': '', 'correct': correct, **({'is_example': True} if index == 0 else {})}
        for index, (before, options, correct) in enumerate([
            ('I ___ a student.', ['am', 'is', 'are'], 0),
            ('My name ___ Sue.', ['am', 'is', 'are'], 1),
            ('I ___ from Uzbekistan.', ['am', 'is', 'are'], 0),
            ('My parents ___ 40 years old.', ['am', 'is', 'are'], 2),
            ('My friends ___ from Germany.', ['am', 'is', 'are'], 2),
            ('The cat ___ very small.', ['am', 'is', 'are'], 1),
            ('They ___ from Germany.', ['am', 'is', 'are'], 2),
            ('We ___ university students.', ['am', 'is', 'are'], 2),
            ('She ___ from Korea.', ['am', 'is', 'are'], 1),
        ])
    ]}
    matching.content = {
        'left': ['I', 'My name', 'He', 'Mary and I', 'My brothers', 'My cat', 'The car', 'The books', 'Tom and Sarah'],
        'right': ['am Natalie.', 'is Sue.', 'is a teacher.', 'are from Italy.', 'are at home.', 'is black and white.', 'is outside.', 'are very interesting.', 'are best friends.'],
        'pairs': list(range(9)),
    }
    for exercise in exercises:
        exercise.source_unit = lesson.order
        exercise.save(update_fields=['content', 'source_unit'])
    return 2


def restore_missing_supplements(lesson):
    current = lesson.exercises.filter(source=SUPPLEMENT_SOURCE).count()
    if current >= 2:
        return 0
    next_order = (lesson.exercises.aggregate(value=Max('order'))['value'] or 0) + 1
    definitions = []
    if lesson.order == 1:
        definitions.append({
            'type': 'matching',
            'content': {
                'left': ['Hello. My name is Natalie.', 'How do you spell Singh?', 'What is your first name?', 'What is your last name?', 'Good morning.', 'Goodbye.'],
                'right': ['Nice to meet you.', 'S-I-N-G-H.', 'Mario.', 'Khan.', 'Good morning.', 'See you later.'],
                'pairs': list(range(6)),
            },
            'kaa': 'Gáplerdi sáykes juwaplar menen juplastırıń.',
            'uz': 'Gaplarni mos javoblar bilan juftlang.',
        })
    elif lesson.order == 5:
        definitions.append({
            'type': 'written_answer',
            'content': {'questions': [
                {'prompt': prompt, 'answer': answer, **({'is_example': True} if index == 0 else {})}
                for index, (prompt, answer) in enumerate([
                    ('___ fish is called Nemo.', 'Her fish is called Nemo.'),
                    ('___ dog is called Beth.', 'Their dog is called Beth.'),
                    ('___ tortoise is 50 years old.', 'His tortoise is 50 years old.'),
                    ('___ cat is called Sam.', 'My cat is called Sam.'),
                    ('___ lion is from Kenya.', 'Our lion is from Kenya.'),
                    ('___ rabbit eats grass.', 'Your rabbit eats grass.'),
                    ('Here is ___ bed.', 'Here is its bed.'),
                ])
            ]},
            'kaa': 'Berilgen tapsırmanı orınlap, tolıq juwaptı inglisshe jazıń.',
            'uz': 'Berilgan topshiriqni bajarib, to‘liq javobni inglizcha yozing.',
        })
    for definition in definitions[:2 - current]:
        Exercise.objects.create(
            lesson=lesson,
            type=definition['type'],
            instruction=definition['kaa'],
            instruction_kaa=definition['kaa'],
            instruction_uz=definition['uz'],
            content=definition['content'],
            order=next_order,
            source=SUPPLEMENT_SOURCE,
            source_unit=lesson.order,
        )
        next_order += 1
    return len(definitions[:2 - current])


def validate_exercise(exercise):
    content = exercise.content or {}
    key, rows = rows_for(content)
    errors = []
    if exercise.type in {'fill_blank', 'reading', 'listening'} and key == 'sentences':
        for index, row in enumerate(rows):
            blanks = str(row.get('text') or row.get('sentence') or '').count('___')
            answers = row.get('answer')
            answer_count = len(answers) if isinstance(answers, list) else int(answers is not None)
            if blanks != answer_count:
                errors.append(f'row {index}: {blanks} blanks / {answer_count} answers')
    if exercise.type in {'matching', 'listening'} and content.get('left'):
        left, right, pairs = content.get('left', []), content.get('right', []), content.get('pairs', [])
        if len(left) != len(pairs) or any(not isinstance(value, int) or value < 0 or value >= len(right) for value in pairs):
            errors.append('invalid matching pairs')
    for index, row in enumerate(rows):
        if isinstance(row, dict) and row.get('options'):
            options = row['options']
            correct = row.get('correct', row.get('correct_index'))
            if len(options) != len({str(value).strip().casefold() for value in options}):
                errors.append(f'row {index}: duplicate options')
            if not isinstance(correct, int) or not 0 <= correct < len(options):
                errors.append(f'row {index}: invalid correct index')
    return errors


class Command(BaseCommand):
    help = 'Barcha topshiriqlarni audit qiladi va aniqlangan strukturaviy/kontent xatolarini tuzatadi.'

    def add_arguments(self, parser):
        parser.add_argument('--dry-run', action='store_true')

    @transaction.atomic
    def handle(self, *args, **options):
        counters = Counter()
        exercises = list(Exercise.objects.select_related('lesson', 'lesson__category').order_by('id'))

        for exercise in exercises:
            content = copy.deepcopy(exercise.content or {})
            changed = False
            content, source_rows_repaired = repair_contextless_source_rows(exercise, content)
            if source_rows_repaired:
                counters['contextless_source_exercises_repaired'] += 1
                changed = True
            key, rows = rows_for(content)

            if exercise.type == 'listening' and key == 'sentences' and rows and all(
                isinstance(row, dict) and row.get('options') for row in rows
            ):
                content.pop('sentences', None)
                content['questions'] = rows
                content['example_count'] = 0
                clips = row_audio_urls(exercise.audio_url, len(rows))
                if clips:
                    content['audio_urls'] = clips
                key, rows = 'questions', content['questions']
                counters['listening_choice_shapes_repaired'] += 1
                changed = True

            if exercise.type == 'reading' and key == 'questions' and rows and all(
                isinstance(row, dict) and not row.get('options') and row.get('sentences') for row in rows
            ):
                content = {
                    **{name: copy.deepcopy(value) for name, value in content.items() if name != 'questions'},
                    'questions': [
                        {
                            'prompt': row.get('question'),
                            'answer': row['sentences'][0].get('answer') or row['sentences'][0].get('text'),
                            **({'is_example': True} if row.get('is_example') else {}),
                        }
                        for row in rows
                    ],
                }
                exercise.type = 'written_answer'
                key, rows = 'questions', content['questions']
                counters['nested_reading_repaired'] += 1
                changed = True

            if exercise.id == 1830 and rows:
                for row in rows:
                    if 'learning your book' in str(row.get('before', '')):
                        row['before'] = row['before'].replace('learning your book', 'writing your book')
                        counters['english_answer_errors_repaired'] += 1
                        changed = True
            if exercise.id == 1930 and rows:
                for row in rows:
                    if 'They were having a discussion outside.' in (row.get('options') or []):
                        row['correct'] = row['options'].index('They were having a discussion outside.')
                        counters['english_answer_errors_repaired'] += 1
                        changed = True

            repair = LISTENING_MATCH_REPAIRS.get(exercise.instruction)
            if exercise.type == 'listening' and repair:
                for field in ('right', 'pairs', 'audio_urls', 'example_count'):
                    if field in repair:
                        content[field] = copy.deepcopy(repair[field])
                exercise.audio_url = repair['audio_url']
                exercise.has_audio = True
                counters['listening_pairs_repaired'] += 1
                changed = True

            missing_answers = MISSING_ANSWER_ROWS.get(exercise.instruction)
            if missing_answers and rows and all(not row.get('answer') for row in rows):
                if len(missing_answers) != len(rows):
                    raise CommandError(f'#{exercise.id}: missing-answer map length mismatch')
                for row, answer in zip(rows, missing_answers):
                    row['answer'] = answer
                counters['missing_answer_exercises_repaired'] += 1
                changed = True

            if rows:
                for row in rows:
                    if isinstance(row, dict):
                        if deduplicate_options(row):
                            counters['duplicate_option_rows_repaired'] += 1
                            changed = True
                        if normalize_multi_blank_row(row, exercise.instruction):
                            counters['multi_blank_rows_repaired'] += 1
                            changed = True

            # Five imports contain a complete example followed by real blanks.
            if exercise.type in {'fill_blank', 'reading', 'listening'} and key == 'sentences' and rows:
                missing_marker = [row for row in rows if '___' not in str(row.get('text') or row.get('sentence') or '')]
                if 0 < len(missing_marker) < len(rows):
                    for row in missing_marker:
                        text = str(row.get('text') or row.get('sentence') or '')
                        answer = str(row.get('answer') or '')
                        if answer and answer in text:
                            row['text'] = text.replace(answer, '___', 1)
                        else:
                            row['text'] = '___'
                    counters['example_markers_repaired'] += len(missing_marker)
                    changed = True

            if exercise.type in {'fill_blank', 'reading'} and key == 'sentences' and rows and all(
                '___' not in str(row.get('text') or row.get('sentence') or '') for row in rows
            ):
                exercise.type = 'written_answer'
                content = written_content(content, rows)
                counters['fill_blank_to_written'] += 1
                changed = True

            if exercise.type == 'listening' and not exercise.audio_url and not any(content.get('audio_urls') or []):
                if content.get('left'):
                    exercise.type = 'matching'
                elif rows and any(row.get('options') for row in rows):
                    exercise.type = 'choose_correct'
                elif rows and all('___' in str(row.get('text') or '') for row in rows):
                    exercise.type = 'fill_blank'
                elif rows:
                    exercise.type = 'written_answer'
                    content = written_content(content, rows)
                else:
                    raise CommandError(f'#{exercise.id}: audiosiz listening turi aniqlanmadi')
                exercise.has_audio = False
                counters['audio_less_listening_retyped'] += 1
                changed = True

            if changed:
                exercise.content = content
                exercise.save(update_fields=['type', 'content', 'has_audio', 'audio_url'])

        # One exact duplicate has no attempts and adds no learning value.
        seen = {}
        for exercise in Exercise.objects.order_by('id'):
            fingerprint = (exercise.lesson_id, exercise.type, json.dumps(exercise.content, sort_keys=True))
            if fingerprint in seen and not exercise.attempts.exists():
                exercise.delete()
                counters['duplicates_deleted'] += 1
            else:
                seen[fingerprint] = exercise.id

        book1 = Lesson.objects.filter(category__name='Book 1 – Beginner')
        to_be = book1.filter(order=2, title__icontains='To be').first()
        if to_be:
            counters['to_be_supplements_repaired'] += repair_to_be_lesson(to_be)
            bad_quiz = Quiz.objects.filter(lesson=to_be, question='She is ___ a girl').first()
            if bad_quiz:
                bad_quiz.question = 'She ___ a girl.'
                bad_quiz.save(update_fields=['question'])
                counters['quiz_questions_repaired'] += 1

        plural = book1.filter(order=7, title__icontains='Koplik').first()
        if plural:
            from quiz.management.commands.generate_coursebook_supplement_exercises import title_specific_definitions
            definitions = title_specific_definitions(plural) or []
            targets = list(plural.exercises.filter(source=SUPPLEMENT_SOURCE).order_by('order', 'id'))
            if len(targets) == len(definitions) == 2:
                for exercise, definition in zip(targets, definitions):
                    exercise.type = definition['type']
                    exercise.instruction = definition['instruction']
                    exercise.instruction_kaa = definition['instruction_kaa']
                    exercise.instruction_uz = definition['instruction_uz']
                    exercise.content = definition['content']
                    exercise.source_unit = plural.order
                    exercise.save(update_fields=['type', 'instruction', 'instruction_kaa', 'instruction_uz', 'content', 'source_unit'])
                counters['plural_supplements_repaired'] += 2

        for lesson in book1.filter(order__in=(1, 5)):
            counters['supplements_restored'] += restore_missing_supplements(lesson)

        # Stable unique ordering prevents admin drag/drop collisions.
        for lesson in Lesson.objects.prefetch_related('exercises'):
            for order, exercise in enumerate(lesson.exercises.all().order_by('order', 'id'), start=1):
                if exercise.order != order:
                    exercise.order = order
                    exercise.save(update_fields=['order'])
                    counters['orders_normalized'] += 1

        failures = []
        for exercise in Exercise.objects.all():
            errors = validate_exercise(exercise)
            if errors:
                failures.append(f'#{exercise.id}: {"; ".join(errors)}')
        if failures:
            raise CommandError('Auditdan o‘tmagan topshiriqlar:\n' + '\n'.join(failures[:50]))

        self.stdout.write(self.style.SUCCESS(
            'Audit muvaffaqiyatli: ' + ', '.join(f'{key}={value}' for key, value in sorted(counters.items()))
        ))
        if options['dry_run']:
            transaction.set_rollback(True)
            self.stdout.write(self.style.WARNING('Dry-run: bazaga yozilmadi.'))
