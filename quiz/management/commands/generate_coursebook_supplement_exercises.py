import json
import random
import re
from pathlib import Path

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.db.models import Max

from courses.management.commands.import_preintermediate_vocabulary import SOURCE_TO_LESSON
from courses.models import Category, Lesson
from quiz.models import Exercise


SOURCE = 'course_book_supplement_v1'
PILOT_SOURCE = 'course_book_pilot_v1'
CATEGORY_NAMES = (
    'Book 1 – Beginner',
    'Book 2 – Elementary',
    'Book 3 – Intermediate',
)

INSTRUCTIONS = {
    'word_order': (
        'Sózlerdi durıs tártipke keltirip, gáplerdi dúziń.',
        'So‘zlarni to‘g‘ri tartibga keltirib, gaplarni tuzing.',
    ),
    'written_answer': (
        'Berilgen tapsırmanı orınlap, tolıq juwaptı inglisshe jazıń.',
        'Berilgan topshiriqni bajarib, to‘liq javobni inglizcha yozing.',
    ),
    'choose_correct': (
        'Hár bir soraw ushın durıs juwaptı tańlań.',
        'Har bir savol uchun to‘g‘ri javobni tanlang.',
    ),
    'matching': (
        'Gáplerdi hám juwaplardı bir-birine sáykeslestiriń.',
        'Gaplar va javoblarni bir-biriga moslashtiring.',
    ),
}


def clean(value):
    value = re.sub(r'\s+', ' ', str(value or '')).strip()
    value = re.sub(r'\s+([,.;:!?])', r'\1', value)
    value = re.sub(r'([.!?])(?=[A-Z])', r'\1 ', value)
    value = re.sub(r"\s+(['’]s)\b", r'\1', value, flags=re.IGNORECASE)
    return value


def unique_rows(rows, key):
    seen = set()
    result = []
    for row in rows:
        marker = clean(key(row)).casefold()
        if marker and marker not in seen:
            seen.add(marker)
            result.append(row)
    return result


def prompt_score(row):
    prompt = clean(row.get('choice_prompt', row.get('prompt', '')))
    if re.fullmatch(r'(?:picture\s*)?\d+\s*___', prompt, flags=re.IGNORECASE):
        return -100
    words = len(prompt.split())
    score = words
    if words >= 4:
        score += 8
    if prompt[-1:] in '.?!':
        score += 3
    if '___' in prompt and words >= 3:
        score += 2
    return score


def fill_sentence(text, answer):
    answers = answer if isinstance(answer, list) else [answer]
    result = clean(text)
    for value in answers:
        result = result.replace('___', clean(value), 1)
    return clean(result)


def exercise_rows(exercise):
    content = exercise.content or {}
    if exercise.type in ('fill_blank', 'reading', 'listening') and content.get('sentences'):
        for row in content['sentences']:
            answer = row.get('answer', '')
            completed = fill_sentence(row.get('text') or row.get('sentence'), answer)
            if completed and '___' not in completed:
                short_answer = ' / '.join(clean(value) for value in answer) if isinstance(answer, list) else clean(answer)
                prompt = clean(row.get('text') or row.get('sentence'))
                yield {
                    'prompt': prompt,
                    'answer': completed,
                    'sentence': completed,
                    'choice_prompt': prompt,
                    'choice_answer': short_answer,
                }

    if exercise.type == 'choose_correct' and content.get('sentences'):
        for row in content['sentences']:
            options = row.get('options') or []
            correct = row.get('correct', row.get('correct_index'))
            if isinstance(correct, int) and 0 <= correct < len(options):
                sentence = clean(f"{row.get('before', '')}{options[correct]}{row.get('after', '')}")
                wrong_options = [option for index, option in enumerate(options) if index != correct]
                wrong = clean(f"{row.get('before', '')}{wrong_options[0]}{row.get('after', '')}") if wrong_options else ''
                yield {
                    'prompt': wrong or sentence,
                    'answer': sentence,
                    'sentence': sentence,
                    'choice_prompt': clean(f"{row.get('before', '')}___{row.get('after', '')}"),
                    'choice_answer': clean(options[correct]),
                }

    questions = content.get('questions') or []
    if questions and exercise.type in ('reading', 'listening'):
        for row in questions:
            options = row.get('options') or []
            correct = row.get('correct', row.get('correct_index'))
            if isinstance(correct, int) and 0 <= correct < len(options):
                question = clean(row.get('question') or row.get('sentence'))
                yield {
                    'prompt': question,
                    'answer': clean(options[correct]),
                    'sentence': question,
                    'choice_prompt': question,
                    'choice_answer': clean(options[correct]),
                }

    left = content.get('left') or []
    right = content.get('right') or []
    pairs = content.get('pairs') or list(range(len(left)))
    if left and right and pairs and isinstance(pairs[0], int):
        for index, left_value in enumerate(left):
            right_index = pairs[index] if index < len(pairs) else index
            if isinstance(right_index, int) and 0 <= right_index < len(right):
                prompt = clean(left_value)
                answer = clean(right[right_index])
                if 'scrambl' in exercise.instruction.lower():
                    prompt, answer = answer, prompt
                yield {
                    'prompt': prompt,
                    'answer': answer,
                    'sentence': clean(f'{prompt} {answer}'),
                    'choice_prompt': prompt,
                    'choice_answer': answer,
                }


def source_rows(lesson):
    rows = []
    exercises = lesson.exercises.exclude(source__startswith='course_book_').order_by('order', 'id')
    for exercise in exercises:
        for row in exercise_rows(exercise):
            row['group'] = exercise.id
            row['priority'] = {
                'choose_correct': 0,
                'fill_blank': 1,
                'reading': 2,
                'listening': 2,
                'matching': 3,
            }.get(exercise.type, 4)
            rows.append(row)
    rows = [row for row in rows if row['prompt'] and row['answer'] and row['sentence']]
    return unique_rows(rows, lambda row: f"{row['prompt']}|{row['answer']}")


def manual_rows(category_name, lesson_order):
    data = {
        ('Book 1 – Beginner', 9): [
            ('doctor — hospital', 'A doctor works in a hospital.', 'Who works in a hospital?', 'a doctor'),
            ('teacher — school', 'A teacher works in a school.', 'Who works in a school?', 'a teacher'),
            ('chef — restaurant', 'A chef works in a restaurant.', 'Who cooks in a restaurant?', 'a chef'),
            ('vet — animals', 'A vet looks after sick animals.', 'Who looks after sick animals?', 'a vet'),
            ('driver — bus', 'A driver drives a bus.', 'Who drives a bus?', 'a driver'),
            ('builder — houses', 'A builder builds houses.', 'Who builds houses?', 'a builder'),
        ],
        ('Book 1 – Beginner', 11): [
            ('08:15', 'It is quarter past eight.', 'What time is 08:15?', 'quarter past eight'),
            ('09:30', 'It is half past nine.', 'What time is 09:30?', 'half past nine'),
            ('10:45', 'It is quarter to eleven.', 'What time is 10:45?', 'quarter to eleven'),
            ('12:05', 'It is five past twelve.', 'What time is 12:05?', 'five past twelve'),
            ('02:50', 'It is ten to three.', 'What time is 02:50?', 'ten to three'),
            ('06:20', 'It is twenty past six.', 'What time is 06:20?', 'twenty past six'),
        ],
        ('Book 1 – Beginner', 12): [
            ('the cat / my brother', "The cat is my brother's.", 'Whose cat is it?', "my brother's"),
            ('the books / the children', "The books are the children's.", 'Whose books are they?', "the children's"),
            ('the tickets / our friends', "The tickets are our friends'.", 'Whose tickets are they?', "our friends'"),
            ('the guitar / Emma', "The guitar is Emma's.", 'Whose guitar is it?', "Emma's"),
            ('the games / James', "The games are James's.", 'Whose games are they?', "James's"),
            ('the television / my parents', "The television is my parents'.", 'Whose television is it?', "my parents'"),
        ],
        ('Book 1 – Beginner', 18): [
            ('work at the hospital / yes', 'She works at the hospital.', 'Does she work at the hospital?', 'Yes, she does.'),
            ('live near the school / no', 'He does not live near the school.', 'Does he live near the school?', "No, he doesn't."),
            ('play tennis / yes', 'They play tennis on Sundays.', 'Do they play tennis on Sundays?', 'Yes, they do.'),
            ('like coffee / no', 'Anna does not like coffee.', 'Does Anna like coffee?', "No, she doesn't."),
            ('study English / yes', 'We study English every day.', 'Do you study English every day?', 'Yes, we do.'),
            ('drive to work / no', 'Tom does not drive to work.', 'Does Tom drive to work?', "No, he doesn't."),
        ],
        ('Book 1 – Beginner', 19): [
            ('school / he', 'He goes to Greenhill School.', 'Which school does he go to?', 'Greenhill School'),
            ('work / she', 'She works at the city hospital.', 'Where does she work?', 'at the city hospital'),
            ('breakfast / they', 'They have breakfast at seven.', 'When do they have breakfast?', 'at seven'),
            ('travel / Maria', 'Maria travels to work by bus.', 'How does Maria travel to work?', 'by bus'),
            ('weekend / you', 'I visit my family at the weekend.', 'What do you do at the weekend?', 'visit my family'),
            ('English / Ben', 'Ben studies English because he needs it for work.', 'Why does Ben study English?', 'because he needs it for work'),
        ],
        ('Book 1 – Beginner', 38): [
            ('Tom / swimming / every Saturday', 'Tom goes swimming every Saturday.', 'What does Tom do every Saturday?', 'goes swimming'),
            ('Sara / tennis / on Sundays', 'Sara plays tennis on Sundays.', 'What does Sara play on Sundays?', 'tennis'),
            ('We / cycling / after work', 'We go cycling after work.', 'What do we do after work?', 'go cycling'),
            ('Jack / basketball / at school', 'Jack plays basketball at school.', 'What does Jack play at school?', 'basketball'),
            ('They / skiing / in winter', 'They go skiing in winter.', 'What do they do in winter?', 'go skiing'),
            ('I / running / every morning', 'I go running every morning.', 'What do I do every morning?', 'go running'),
        ],
        ('Book 1 – Beginner', 40): [
            ('Shelley / reading / love', 'Shelley loves reading by the sea.', 'What does Shelley love doing?', 'reading by the sea'),
            ('Mark / crowded cafés / dislike', 'Mark dislikes crowded cafés.', 'What does Mark dislike?', 'crowded cafés'),
            ('We / dancing / enjoy', 'We enjoy dancing at the weekend.', 'What do we enjoy doing?', 'dancing at the weekend'),
            ('I / early mornings / hate', 'I hate getting up early.', 'What do I hate doing?', 'getting up early'),
            ('They / Italian food / like', 'They like eating Italian food.', 'What do they like eating?', 'Italian food'),
            ('Sara / football / not like', 'Sara does not like watching football.', 'What does Sara not like watching?', 'football'),
        ],
        ('Book 1 – Beginner', 48): [
            ('Doug / learn French', 'Doug would quite like to learn French.', 'What would Doug like to learn?', 'French'),
            ('Edith / read a new book', 'Edith would really like to read a new book.', 'What would Edith like to read?', 'a new book'),
            ('I / study abroad', 'I would love to study abroad next year.', 'Where would I love to study?', 'abroad'),
            ('We / take an evening class', 'We would like to take an evening class.', 'What would we like to take?', 'an evening class'),
            ('Mia / improve her writing', 'Mia wants to improve her English writing.', 'What does Mia want to improve?', 'her English writing'),
            ('They / practise every day', 'They plan to practise English every day.', 'What do they plan to do every day?', 'practise English'),
        ],
        ('Book 2 – Elementary', 10): [
            ('It joins your foot to your leg.', 'The ankle joins the foot to the leg.', 'Which body part joins the foot to the leg?', 'ankle'),
            ('You use it to see.', 'You use your eyes to see.', 'Which body parts do you use to see?', 'eyes'),
            ('It is at the end of your arm.', 'Your hand is at the end of your arm.', 'Which body part is at the end of your arm?', 'hand'),
            ('They form the edge of your mouth.', 'Your lips form the edge of your mouth.', 'Which body parts form the edge of your mouth?', 'lips'),
            ('It connects your head to your body.', 'Your neck connects your head to your body.', 'Which body part connects the head to the body?', 'neck'),
            ('You use them to hear.', 'You use your ears to hear.', 'Which body parts do you use to hear?', 'ears'),
        ],
        ('Book 3 – Intermediate', 20): [
            ('learn English / three years', 'I have been learning English for three years.', 'How long have you been learning English?', 'for three years'),
            ('write the book / January', 'She has been writing her book since January.', 'How long has she been writing her book?', 'since January'),
            ('play the piano / childhood', 'He has been playing the piano since childhood.', 'How long has he been playing the piano?', 'since childhood'),
            ('train for the race / six months', 'They have been training for the race for six months.', 'How long have they been training?', 'for six months'),
            ('work on this project / Monday', 'We have been working on this project since Monday.', 'How long have you been working on this project?', 'since Monday'),
            ('practise painting / two hours', 'Mia has been practising painting for two hours.', 'How long has Mia been practising painting?', 'for two hours'),
        ],
        ('Book 3 – Intermediate', 33): [
            ('open the window', 'Could you open the window, please?', 'Which request is more polite?', 'Could you open the window, please?'),
            ('borrow a pen', 'May I borrow your pen, please?', 'How can you politely ask for a pen?', 'May I borrow your pen, please?'),
            ('turn down the music', 'Would you mind turning down the music?', 'How can you politely ask about the music?', 'Would you mind turning down the music?'),
            ('use the phone', 'Would it be all right if I used your phone?', 'How can you politely ask to use the phone?', 'Would it be all right if I used your phone?'),
            ('help with the bags', 'Could you help me with these bags?', 'How can you politely ask for help?', 'Could you help me with these bags?'),
            ('leave a little early', 'Do you mind if I leave a little early?', 'How can you politely ask to leave early?', 'Do you mind if I leave a little early?'),
        ],
        ('Book 3 – Intermediate', 46): [
            ('discussion / outside', 'They were having a discussion outside.', 'What were they doing outside?', 'having a discussion'),
            ('dinner / phone rang', 'I was making dinner when the phone rang.', 'What were you doing when the phone rang?', 'making dinner'),
            ('notes / teacher spoke', 'The students were taking notes while the teacher spoke.', 'What were the students doing?', 'taking notes'),
            ('walk / rain started', 'We were taking a walk when it started to rain.', 'What were you doing when it started to rain?', 'taking a walk'),
            ('homework / lights went out', 'Leo was doing his homework when the lights went out.', 'What was Leo doing?', 'doing his homework'),
            ('photos / parade passed', 'Sara was taking photos while the parade passed.', 'What was Sara doing?', 'taking photos'),
        ],
        ('Book 3 – Intermediate', 53): [
            ('finish work / call Anna', 'After I had finished work, I called Anna.', 'What did you do after you had finished work?', 'called Anna'),
            ('train leave / station', 'The train had already left when we reached the station.', 'What had happened before you reached the station?', 'the train had left'),
            ('eat dinner / movie', 'They watched a movie after they had eaten dinner.', 'What did they do after dinner?', 'watched a movie'),
            ('lock door / go to bed', 'She had locked the door before she went to bed.', 'What had she done before going to bed?', 'locked the door'),
            ('rain stop / leave', 'We left the house after the rain had stopped.', 'When did you leave the house?', 'after the rain had stopped'),
            ('read email / reply', 'Ben replied as soon as he had read the email.', 'When did Ben reply?', 'after he had read the email'),
        ],
        ('Book 3 – Intermediate', 56): [
            ('late bus / explain', 'Maya explained that the bus had been late.', 'Why was Maya late?', 'the bus had been late'),
            ('new plan / suggest', 'Tom suggested trying the new plan.', 'What did Tom suggest?', 'trying the new plan'),
            ('broken window / admit', 'Leo admitted breaking the window.', 'What did Leo admit?', 'breaking the window'),
            ('finish report / promise', 'Sara promised to finish the report.', 'What did Sara promise?', 'to finish the report'),
            ('earlier train / recommend', 'The guide recommended taking an earlier train.', 'What did the guide recommend?', 'taking an earlier train'),
            ('wrong address / point out', 'Anna pointed out that we had the wrong address.', 'What did Anna point out?', 'we had the wrong address'),
        ],
    }.get((category_name, lesson_order))
    if not data:
        return None
    return [
        {
            'prompt': prompt,
            'answer': answer,
            'sentence': answer,
            'choice_prompt': choice_prompt,
            'choice_answer': choice_answer,
            'group': f'manual-{category_name}-{lesson_order}',
            'priority': 0,
        }
        for prompt, answer, choice_prompt, choice_answer in data
    ]


def word_order_content(rows, rng):
    def is_sentence(value):
        value = clean(value)
        return (
            4 <= len(value.split()) <= 18
            and value[:1].isupper()
            and value[-1:] in '.?!'
            and not any(marker in value for marker in ('[', ']', '___', '`', '—'))
        )

    candidates = unique_rows(
        [row for row in rows if is_sentence(row['sentence'])],
        lambda row: row['sentence'],
    )
    candidates.sort(key=lambda row: (row.get('priority', 9), -prompt_score(row)))
    if len(candidates) < 2:
        return None
    selected = candidates[:6]
    items = []
    for row in selected:
        tokens = row['sentence'].split()
        if len(tokens) < 2:
            continue
        items.append({'tokens': tokens, 'answer': row['sentence']})
    if len(items) < 2:
        return None
    return {'items': items, 'variation_seed': rng.randint(1, 999999)}


def written_content(rows):
    groups = {}
    for row in rows:
        groups.setdefault(row.get('group'), []).append(row)
    selected = max(
        (group_rows for group_rows in groups.values() if len(group_rows) >= 2),
        key=lambda group_rows: sum(prompt_score(row) for row in group_rows) / len(group_rows),
        default=rows,
    )
    selected = unique_rows(selected, lambda row: row['prompt'])[:7]
    questions = [
        {'prompt': row['prompt'], 'answer': row['answer'], 'alternatives': []}
        for row in selected
    ]
    return {'questions': questions} if len(questions) >= 2 else None


def matching_content(rows):
    groups = {}
    for row in rows:
        groups.setdefault(row.get('group'), []).append(row)
    selected = []
    ordered_groups = sorted(
        groups.values(),
        key=lambda group_rows: sum(prompt_score(row) for row in group_rows) / len(group_rows),
        reverse=True,
    )
    for group_rows in ordered_groups:
        coherent = unique_rows(group_rows, lambda row: row.get('choice_answer', row['answer']))
        coherent = unique_rows(coherent, lambda row: row.get('choice_prompt', row['prompt']))
        if len(coherent) >= 2:
            selected = coherent[:7]
            break
    if len(selected) < 2:
        return None
    return {
        'left': [row.get('choice_prompt', row['prompt']) for row in selected],
        'right': [row.get('choice_answer', row['answer']) for row in selected],
        'pairs': list(range(len(selected))),
    }


def choose_content(rows, rng):
    groups = {}
    for row in rows:
        groups.setdefault(row.get('group'), []).append(row)

    selected_group = None
    answer_pool = []
    ordered_groups = sorted(
        groups.values(),
        key=lambda group_rows: sum(prompt_score(row) for row in group_rows) / len(group_rows),
        reverse=True,
    )
    for group_rows in ordered_groups:
        pool = []
        usable_rows = []
        for row in group_rows:
            answer = row.get('choice_answer', row['answer'])
            prompt = row.get('choice_prompt', row['prompt'])
            if len(answer) <= 90 and prompt_score(row) > -100:
                usable_rows.append(row)
                if answer not in pool:
                    pool.append(answer)
        if len(pool) >= 2:
            selected_group = usable_rows
            answer_pool = pool
            break
    if not selected_group:
        return None

    sentences = []
    for index, row in enumerate(selected_group):
        correct = row.get('choice_answer', row['answer'])
        if correct not in answer_pool or len(correct) > 90:
            continue
        distractors = [answer for answer in answer_pool if answer != correct]
        rng.shuffle(distractors)
        options = [correct, *distractors[:3]]
        rng.shuffle(options)
        sentences.append({
            'before': row.get('choice_prompt', row['prompt']),
            'options': options,
            'after': '',
            'correct': options.index(correct),
            'is_example': index == 0,
        })
        if len(sentences) == 6:
            break
    return {'sentences': sentences} if len(sentences) >= 2 else None


BUILDERS = {
    'matching': matching_content,
    'written_answer': written_content,
}


def source_unit_for(category_name, lesson_order):
    if category_name != 'Book 3 – Intermediate':
        return lesson_order
    units = [source for source, target in SOURCE_TO_LESSON.items() if target == lesson_order]
    return min(units) if units else lesson_order


def build_definitions(lesson):
    rows = manual_rows(lesson.category.name, lesson.order) or source_rows(lesson)
    if len(rows) < 2:
        raise CommandError(f'Yetarli manba topilmadi: lesson={lesson.id} {lesson.title}')

    rng = random.Random(f'course-book-supplement-{lesson.id}-{lesson.order}')
    first_content = word_order_content(rows, rng)
    if not first_content:
        first_content = choose_content(rows, rng)
        first_type = 'choose_correct'
    else:
        first_type = 'word_order'

    preferred = ('choose_correct', 'matching', 'written_answer')[lesson.order % 3]
    if preferred == first_type:
        preferred = 'matching' if first_type != 'matching' else 'written_answer'
    if preferred == 'choose_correct':
        second_content = choose_content(rows, rng)
    else:
        second_content = BUILDERS[preferred](rows)

    if not second_content:
        fallbacks = (
            ('matching', matching_content(rows)),
            ('written_answer', written_content(rows)),
            ('choose_correct', choose_content(rows, rng)),
        )
        preferred, second_content = next(
            (exercise_type, content) for exercise_type, content in fallbacks if content
        )

    definitions = []
    for exercise_type, content in ((first_type, first_content), (preferred, second_content)):
        kaa, uz = INSTRUCTIONS[exercise_type]
        definitions.append({
            'type': exercise_type,
            'instruction': kaa,
            'instruction_kaa': kaa,
            'instruction_uz': uz,
            'content': content,
        })
    return definitions


def title_specific_definitions(lesson):
    """Serverda eski importdan qolgan, kitob unitidan farq qiladigan darslar."""
    titles = ' '.join(filter(None, (lesson.title, lesson.title_kaa, lesson.title_uz))).casefold()
    if lesson.category.name == 'Book 1 – Beginner' and ('koplik' in titles or 'ko\u02bbplik' in titles):
        data = [
            ('one book / two books', 'There are two books on the table.', 'What is the plural of “book”?', 'books'),
            ('one child / three children', 'Three children are playing outside.', 'What is the plural of “child”?', 'children'),
            ('one woman / two women', 'Two women work in this office.', 'What is the plural of “woman”?', 'women'),
            ('one box / four boxes', 'There are four boxes by the door.', 'What is the plural of “box”?', 'boxes'),
            ('one city / many cities', 'Many cities have large parks.', 'What is the plural of “city”?', 'cities'),
            ('one person / five people', 'Five people are waiting for the bus.', 'What is the plural of “person”?', 'people'),
        ]
        rows = [
            {
                'prompt': prompt,
                'answer': answer,
                'sentence': answer,
                'choice_prompt': choice_prompt,
                'choice_answer': choice_answer,
                'group': 'manual-server-plurals',
                'priority': 0,
            }
            for prompt, answer, choice_prompt, choice_answer in data
        ]
        rng = random.Random(f'course-book-server-special-{lesson.id}')
        definitions = []
        for exercise_type, content in (
            ('word_order', word_order_content(rows, rng)),
            ('choose_correct', choose_content(rows, rng)),
        ):
            kaa, uz = INSTRUCTIONS[exercise_type]
            definitions.append({
                'type': exercise_type,
                'instruction': kaa,
                'instruction_kaa': kaa,
                'instruction_uz': uz,
                'content': content,
            })
        return definitions
    return None


class Command(BaseCommand):
    help = 'Barcha Book 1–3 darslariga ikki xil Course Book qo‘shimcha mashq yaratadi.'

    def add_arguments(self, parser):
        parser.add_argument('--dry-run', action='store_true')
        parser.add_argument('--replace', action='store_true')
        parser.add_argument(
            '--fixture',
            help='Oldindan tekshirilgan JSON topshiriqlarni import qilish (server bazasi uchun).',
        )

    @transaction.atomic
    def handle(self, *args, **options):
        fixture_map = None
        if options['fixture']:
            fixture_path = Path(options['fixture'])
            try:
                fixture_rows = json.loads(fixture_path.read_text(encoding='utf-8'))
                fixture_map = {
                    (row['category'], int(row['lesson_order'])): row['exercises']
                    for row in fixture_rows
                }
            except (OSError, ValueError, KeyError, TypeError) as exc:
                raise CommandError(f'Fixture o\u02bbqilmadi: {exc}') from exc

        if options['replace']:
            deleted, _ = Exercise.objects.filter(source=SOURCE).delete()
            self.stdout.write(f'Oldingi ommaviy qo‘shimchalar: {deleted} ta o‘chirildi.')

        categories = {
            category.name: category
            for category in Category.objects.filter(name__in=CATEGORY_NAMES)
        }
        missing = [name for name in CATEGORY_NAMES if name not in categories]
        if missing:
            raise CommandError(f"Kategoriyalar topilmadi: {', '.join(missing)}")

        created = []
        skipped_pilots = 0
        for category_name in CATEGORY_NAMES:
            lessons = Lesson.objects.filter(category=categories[category_name]).order_by('order', 'id')
            for lesson in lessons:
                if lesson.exercises.filter(source=PILOT_SOURCE).exists():
                    skipped_pilots += 1
                    continue

                specific_definitions = title_specific_definitions(lesson)
                if specific_definitions:
                    definitions = specific_definitions
                elif fixture_map is None:
                    definitions = build_definitions(lesson)
                else:
                    definitions = fixture_map.get((category_name, lesson.order))
                    if not definitions:
                        raise CommandError(
                            f'Fixture ichida dars topilmadi: {category_name}, unit {lesson.order}'
                        )
                if len(definitions) != 2:
                    raise CommandError(
                        f'Har bir darsda 2 ta topshiriq bo\u02bblishi kerak: '
                        f'{category_name}, unit {lesson.order}'
                    )
                next_order = (lesson.exercises.aggregate(value=Max('order'))['value'] or 0) + 1
                source_unit = source_unit_for(category_name, lesson.order)
                for offset, definition in enumerate(definitions):
                    created.append(Exercise.objects.create(
                        lesson=lesson,
                        order=next_order + offset,
                        source=SOURCE,
                        source_unit=source_unit,
                        **definition,
                    ))

        counts = {
            exercise_type: sum(item.type == exercise_type for item in created)
            for exercise_type in ('word_order', 'written_answer', 'choose_correct', 'matching')
        }
        self.stdout.write(self.style.SUCCESS(
            f'{len(created)} ta yangi topshiriq yaratildi; {skipped_pilots} ta pilot dars saqlandi. '
            + ', '.join(f'{key}={value}' for key, value in counts.items())
        ))
        if options['dry_run']:
            transaction.set_rollback(True)
            self.stdout.write(self.style.WARNING('Dry-run: bazaga yozilmadi.'))
