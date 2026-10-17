"""Import all Level 2 Practice Book units into the A2 curriculum.

The importer works unit-by-unit so multi-page readings remain a single
exercise. It is idempotent: a successfully reprocessed unit replaces only its
own exercises, while lessons and their A2 mapping are updated in place.
"""
import base64
from concurrent.futures import ThreadPoolExecutor, as_completed
import json
import re
import shutil
import subprocess
import time
from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction


BOOK_PDF = Path(settings.BASE_DIR) / 'dk_english_for_everyone_level_2_beginner_practice_book.pdf'
SOURCE_DIR = Path(settings.BASE_DIR) / 'scratch' / 'book2_pages'
STATIC_DIR = Path(settings.BASE_DIR) / 'static' / 'book2'
PROGRESS_FILE = Path(settings.BASE_DIR) / 'seed_book2_progress.json'
STATIC_NAME = 'English_for_Everyone_Level_2_Practice_Book_page-{page:04d}.jpg'

# Printed/PDF page numbers from the book's contents. Vocabulary sections are
# kept as their own short lessons, matching the book's learning sequence.
UNIT_STARTS = [
    (12, 'Talking about yourself'),
    (14, 'Talking about routines'),
    (18, 'Today I’m wearing…'),
    (22, 'What’s happening?'),
    (26, 'Types of verbs'),
    (28, 'Vocabulary: Feelings and moods'),
    (30, 'How are you feeling?'),
    (34, 'Vocabulary: Transportation'),
    (36, 'Routines and exceptions'),
    (38, 'Vocabulary: The body'),
    (40, 'What’s the matter?'),
    (42, 'Vocabulary: Weather'),
    (44, 'What’s the weather like?'),
    (46, 'Vocabulary: Travel'),
    (48, 'Making comparisons'),
    (52, 'Talking about extremes'),
    (56, 'Vocabulary: Geographical features'),
    (58, 'Making choices'),
    (62, 'Using large numbers'),
    (64, 'Vocabulary: The calendar'),
    (66, 'Talking about dates'),
    (68, 'Talking about the past'),
    (72, 'Past events'),
    (76, 'Past abilities'),
    (78, 'Vocabulary: Entertainment'),
    (80, 'Irregular past verbs'),
    (84, 'Vocabulary: Tools'),
    (86, 'Telling a story'),
    (90, 'Asking about the past'),
    (94, 'Applying for a job'),
    (96, 'Types of questions'),
    (100, 'Someone, anyone, everyone'),
    (102, 'Making conversation'),
    (104, 'Vocabulary: Going out'),
    (106, 'Future arrangements'),
    (110, 'Plans and intentions'),
    (114, 'What’s going to happen?'),
    (118, 'Vocabulary: Animals'),
    (120, 'Making predictions'),
    (124, 'Making quick decisions'),
    (128, 'Future possibilities'),
    (132, 'Giving advice'),
    (134, 'Making suggestions'),
    (136, 'Vocabulary: Household chores'),
    (138, 'Around the house'),
    (142, 'Events in your life'),
    (146, 'Events in your year'),
    (150, 'Eating out'),
    (152, 'Achievements and ambitions'),
]

# A few two-page vocabulary spreads contain only pictograms plus a word panel.
# The model can correctly decide that the original picture-writing activity is
# unsupported and return nothing. These deterministic, page-derived matching
# tasks keep those lessons useful without requiring the omitted pictograms.
VOCAB_FALLBACKS = {
    12: (
        'Match each weather definition to the correct word.',
        [
            ('A white or gray mass in the sky', 'cloud'),
            ('Water drops falling from clouds', 'rain'),
            ('Soft frozen flakes falling from the sky', 'snow'),
            ('A flash of electricity in the sky', 'lightning'),
            ('The loud sound that follows lightning', 'thunder'),
            ('An arc of colors seen after rain', 'rainbow'),
            ('A very strong wind', 'gale'),
            ('Water covering land that is normally dry', 'flood'),
        ],
    ),
    25: (
        'Match each entertainment definition to the correct word.',
        [
            ('A long fictional book', 'novel'),
            ('A program shown on television', 'TV show'),
            ('A person who writes books', 'author'),
            ('A person who controls the making of a movie', 'director'),
            ('A funny movie or play', 'comedy'),
            ('A frightening story or movie', 'horror'),
            ('The people watching a performance', 'audience'),
            ('A shop that sells books', 'bookstore'),
        ],
    ),
    44: (
        'Match each household chore to its meaning.',
        [
            ('Put plates and cutlery on the table before a meal', 'set the table'),
            ('Clean a carpet with an electric machine', 'vacuum the carpet'),
            ('Use an iron to remove wrinkles from clothes', 'do the ironing'),
            ('Give food to animals at home', 'feed the pets'),
            ('Cut food into small pieces', 'chop vegetables'),
            ('Put dirty plates into a washing machine', 'load the dishwasher'),
            ('Cut the grass in the yard', 'mow the lawn'),
            ('Put clean clothes into neat shapes', 'fold clothes'),
        ],
    ),
}


def fallback_exercise(unit_number):
    definition = VOCAB_FALLBACKS.get(unit_number)
    if not definition:
        return []
    instruction, rows = definition
    return [{
        'type': 'matching',
        'instruction': instruction,
        'source_pages': [],
        'content': {
            'left': [left for left, _ in rows],
            'right': [right for _, right in rows],
            'pairs': list(range(len(rows))),
        },
    }]


def unit_definitions():
    rows = []
    for index, (start_page, title) in enumerate(UNIT_STARTS):
        end_page = UNIT_STARTS[index + 1][0] - 1 if index + 1 < len(UNIT_STARTS) else 155
        rows.append({
            'number': index + 1,
            'title': title,
            'start_page': start_page,
            'end_page': end_page,
        })
    return rows


def parse_range(value, maximum):
    match = re.fullmatch(r'\s*(\d+)(?:-(\d+))?\s*', value or '')
    if not match:
        raise CommandError('Unit oralig‘i 1-10 yoki 7 ko‘rinishida bo‘lishi kerak.')
    start = int(match.group(1))
    end = int(match.group(2) or start)
    if start < 1 or end > maximum or start > end:
        raise CommandError(f'Unit oralig‘i 1-{maximum} ichida bo‘lishi kerak.')
    return start, end


def page_source_path(page):
    candidates = [
        SOURCE_DIR / f'page-{page}.jpg',
        SOURCE_DIR / f'page-{page:03d}.jpg',
        SOURCE_DIR / f'page-{page:04d}.jpg',
    ]
    return next((path for path in candidates if path.exists()), None)


def image_data_url(path):
    return 'data:image/jpeg;base64,' + base64.b64encode(path.read_bytes()).decode('ascii')


def extract_json(value):
    text = value.strip()
    if '```json' in text:
        text = text.split('```json', 1)[1].split('```', 1)[0]
    elif '```' in text:
        text = text.split('```', 1)[1].split('```', 1)[0]
    return json.loads(text.strip())


def prompt_for_unit(unit):
    return f"""You are extracting accurate, interactive A2 English exercises
from English for Everyone Level 2 Practice Book.

The attached images are all pages of section {unit['number']},
"{unit['title']}" (pages {unit['start_page']}–{unit['end_page']}). Analyze them together.

Return only exercises that work in these exact JSON formats:
1. choose_correct:
   {{"sentences":[{{"before":"She ","options":["is","are"],"after":" ready.","correct":0}}]}}
2. fill_blank:
   {{"sentences":[{{"text":"She ___ ready.","answer":"is"}}],"word_panel":["is","are"]}}
3. matching:
   {{"left":["left"],"right":["right"],"pairs":[0]}}
4. reading, for an article, email, advert, menu, story, or other passage:
   {{"passage_title":"...","questions":[{{"question":"...","options":["..."],"correct":0}}]}}
   or {{"passage_title":"...","sentences":[{{"text":"... ___ ...","answer":"..."}}]}}

Rules:
- Solve every retained item accurately.
- Keep at least two answerable items; item 1 is used as a solved example.
- Use exactly ___ for a fill-in blank and a single string answer per row.
- Skip listening because Level 2 audio was not supplied.
- Skip speaking-only, free-writing, diagram-only, crossword, and word-search tasks.
- Convert vocabulary pages that pair printed words with pictures into self-contained
  textual matching, choose_correct, or fill_blank exercises. Never require the
  learner to see an omitted picture to answer them.
- Return at least one self-contained text exercise for this section. When every
  printed activity is an unsupported visual/speaking format, adapt its printed
  target language and vocabulary into a short matching or fill_blank exercise;
  use only language actually visible on the supplied pages.
- For a reading, include every relevant page number in source_pages and keep multi-page reading as one exercise.
- For other exercise types source_pages may be empty.
- Do not invent unrelated material or include answer-key pages.

Return only valid JSON:
{{"exercises":[{{"type":"fill_blank","instruction":"Fill in the gaps","source_pages":[],"content":{{"sentences":[{{"text":"Example ___","answer":"answer"}},{{"text":"Question ___","answer":"answer"}}]}}}}]}}
"""


def normalize_content(content):
    result = dict(content or {})
    for key in ('sentences', 'questions'):
        rows = result.get(key)
        if not isinstance(rows, list):
            continue
        normalized = []
        for index, row in enumerate(rows):
            if not isinstance(row, dict):
                continue
            item = dict(row)
            if 'correct' in item:
                try:
                    item['correct'] = int(item['correct'])
                except (TypeError, ValueError):
                    item['correct'] = 0
            if index == 0:
                item['is_example'] = True
            normalized.append(item)
        result[key] = normalized
    if isinstance(result.get('pairs'), list):
        try:
            result['pairs'] = [int(value) for value in result['pairs']]
        except (TypeError, ValueError):
            result['pairs'] = []
    return result


def item_count(exercise_type, content):
    if exercise_type == 'matching':
        return len(content.get('left') or [])
    return len(content.get('sentences') or content.get('questions') or [])


class Command(BaseCommand):
    help = 'Level 2 Practice Book’ning 49 bo‘limini A2 leveliga import qiladi'

    def add_arguments(self, parser):
        parser.add_argument('--clear', action='store_true')
        parser.add_argument('--render', action='store_true')
        parser.add_argument('--units', default='1-49')
        parser.add_argument('--delay', type=float, default=1.0)
        parser.add_argument('--workers', type=int, default=4)
        parser.add_argument('--retry-skipped', action='store_true')
        parser.add_argument('--status', action='store_true')

    def handle(self, *args, **options):
        from decouple import config as env
        from langchain_core.messages import HumanMessage
        from langchain_google_genai import ChatGoogleGenerativeAI

        from courses.models import Category, Lesson, Level
        from quiz.models import Exercise

        definitions = unit_definitions()
        if options['status']:
            self._print_status(definitions)
            return
        if not BOOK_PDF.exists():
            raise CommandError(f'PDF topilmadi: {BOOK_PDF}')
        if options['render']:
            self._render_pages()

        start_unit, end_unit = parse_range(options['units'], len(definitions))
        selected = definitions[start_unit - 1:end_unit]
        missing = [
            page for unit in selected
            for page in range(unit['start_page'], unit['end_page'] + 1)
            if page_source_path(page) is None
        ]
        if missing:
            raise CommandError(
                f'{len(missing)} ta JPG sahifa topilmadi. Avval --render ishlating. '
                f'Birinchi yo‘q sahifa: {missing[0]}'
            )

        api_key = env('GEMINI_API_KRY', default=None) or env('GEMINI_API_KEY', default=None)
        if not api_key:
            raise CommandError('GEMINI_API_KEY yoki GEMINI_API_KRY topilmadi.')
        model = ChatGoogleGenerativeAI(
            model=env('GEMINI_MODEL', default='gemini-2.5-flash'),
            google_api_key=api_key,
            temperature=0.05,
            max_output_tokens=65536,
            timeout=150,
        )

        a2, _ = Level.objects.get_or_create(slug='a2', defaults={'order': 2})
        category, _ = Category.objects.get_or_create(
            name='Book 2 – Elementary',
            defaults={'description': 'DK English for Everyone Level 2 Practice Book (A2)'},
        )
        if options['clear']:
            with transaction.atomic():
                Lesson.objects.filter(title__startswith='[Book 2]').delete()
            if PROGRESS_FILE.exists():
                PROGRESS_FILE.unlink()
            if STATIC_DIR.exists():
                shutil.rmtree(STATIC_DIR)

        lessons = {}
        for unit in definitions:
            title = f"[Book 2] Unit {unit['number']:02d} — {unit['title']}"
            lesson, _ = Lesson.objects.update_or_create(
                title__startswith=f"[Book 2] Unit {unit['number']:02d}",
                defaults={
                    'title': title,
                    'description': (
                        'DK English for Everyone Level 2 Practice Book, '
                        f"section {unit['number']}, pages {unit['start_page']}–{unit['end_page']}"
                    ),
                    'video_url': None,
                    'category': category,
                    'order': unit['number'],
                },
            )
            lesson.levels.set([a2])
            lessons[unit['number']] = lesson

        progress = self._load_progress()
        pending = []
        for unit in selected:
            previous = progress.get('done', {}).get(str(unit['number']))
            lesson_has_exercises = lessons[unit['number']].exercises.exists()
            if ((previous == 'ok' and lesson_has_exercises)
                    or (previous == 'skipped' and not options['retry_skipped'])):
                self.stdout.write(f"  ⏭ Unit {unit['number']:02d} — {previous}")
                continue
            pending.append(unit)

        def analyze(unit):
            paths = [
                page_source_path(page)
                for page in range(unit['start_page'], unit['end_page'] + 1)
            ]
            message_content = [{'type': 'text', 'text': prompt_for_unit(unit)}]
            message_content.extend({
                'type': 'image_url',
                'image_url': {'url': image_data_url(path)},
            } for path in paths)
            self.stdout.write(
                f"  📘 Unit {unit['number']:02d} — {unit['title']} "
                f"({unit['start_page']}–{unit['end_page']})"
            )
            data = self._call_model(model, HumanMessage(content=message_content))
            return unit, data

        workers = max(1, min(options['workers'], 6))
        with ThreadPoolExecutor(max_workers=workers) as executor:
            futures = [executor.submit(analyze, unit) for unit in pending]
            for future in as_completed(futures):
                unit, data = future.result()
                if options['delay'] > 0:
                    time.sleep(options['delay'])
                if not data:
                    self._mark_progress(progress, unit['number'], 'skipped')
                    continue
                exercises = self._normalize_exercises(data.get('exercises') or [], unit)
                if not exercises:
                    exercises = self._normalize_exercises(fallback_exercise(unit['number']), unit)
                if not exercises:
                    self.stderr.write('     Mos interaktiv topshiriq topilmadi; qayta urinish uchun skipped.')
                    self._mark_progress(progress, unit['number'], 'skipped')
                    continue
                with transaction.atomic():
                    lesson = lessons[unit['number']]
                    Exercise.objects.filter(lesson=lesson).delete()
                    for order, definition in enumerate(exercises, start=1):
                        Exercise.objects.create(
                            lesson=lesson,
                            type=definition['type'],
                            instruction=definition['instruction'],
                            content=definition['content'],
                            has_audio=False,
                            audio_url=None,
                            order=order,
                        )
                reading_count = sum(row['type'] == 'reading' for row in exercises)
                self.stdout.write(self.style.SUCCESS(
                    f'     {len(exercises)} topshiriq, {reading_count} reading'
                ))
                self._mark_progress(progress, unit['number'], 'ok')

        lessons_qs = Lesson.objects.filter(title__startswith='[Book 2]')
        exercises_qs = Exercise.objects.filter(lesson__in=lessons_qs)
        self.stdout.write(self.style.SUCCESS(
            f'Tugadi: {lessons_qs.count()} A2 dars, {exercises_qs.count()} topshiriq, '
            f"{exercises_qs.filter(type='reading').count()} reading."
        ))

    def _render_pages(self):
        SOURCE_DIR.mkdir(parents=True, exist_ok=True)
        subprocess.run([
            'pdftoppm', '-f', '12', '-l', '155', '-jpeg', '-r', '130',
            '-jpegopt', 'quality=84,optimize=y', str(BOOK_PDF), str(SOURCE_DIR / 'page'),
        ], check=True)

    def _call_model(self, model, message):
        for attempt in range(1, 6):
            try:
                return extract_json(model.invoke([message]).content)
            except Exception as error:
                retryable = any(term in str(error).lower() for term in (
                    '429', 'quota', 'resource_exhausted', '503', 'unavailable', 'overloaded',
                ))
                # A model can occasionally truncate otherwise valid JSON. A fresh
                # response generally fixes that, so parsing failures get retries too.
                parse_error = isinstance(error, (json.JSONDecodeError, KeyError, TypeError))
                if (not retryable and not parse_error) or attempt == 5:
                    self.stderr.write(f'     AI xatosi: {error}')
                    return None
                wait = 5 * attempt if parse_error else 20 * attempt
                self.stdout.write(f'     Server band, {wait} soniyadan keyin qayta urinish...')
                time.sleep(wait)
        return None

    def _normalize_exercises(self, raw_exercises, unit):
        allowed = {'choose_correct', 'fill_blank', 'matching', 'reading'}
        visual_terms = (
            'picture', 'pictures', 'image', 'images', 'diagram', 'chart',
            'map', 'photo', 'illustration', 'look at the',
        )
        result = []
        fingerprints = set()
        for raw in raw_exercises:
            if not isinstance(raw, dict) or not isinstance(raw.get('content'), dict):
                continue
            exercise_type = raw.get('type')
            instruction = (raw.get('instruction') or '').strip() or 'Complete the exercise'
            if exercise_type not in allowed:
                continue
            if exercise_type != 'reading' and any(term in instruction.lower() for term in visual_terms):
                continue
            content = normalize_content(raw['content'])
            if item_count(exercise_type, content) < 2:
                continue
            if exercise_type == 'matching':
                left = content.get('left') or []
                right = content.get('right') or []
                pairs = content.get('pairs') or []
                if len(right) < 2 or len(pairs) != len(left) or any(
                    index < 0 or index >= len(right) for index in pairs
                ):
                    continue
            if exercise_type == 'fill_blank':
                rows = content.get('sentences') or []
                if any(
                    not isinstance(row.get('answer'), str) or '___' not in str(row.get('text', ''))
                    for row in rows
                ):
                    continue
            source_pages = sorted({
                int(page) for page in (raw.get('source_pages') or [])
                if str(page).isdigit()
                and unit['start_page'] <= int(page) <= unit['end_page']
            })
            if exercise_type == 'reading':
                if not source_pages:
                    continue
                pages = []
                for page in source_pages:
                    source = page_source_path(page)
                    destination = STATIC_DIR / STATIC_NAME.format(page=page)
                    destination.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(source, destination)
                    pages.append({
                        'url': f'/static/book2/{destination.name}',
                        'page_number': page,
                        'caption': f'Level 2 Practice Book — {page}-sahifa',
                    })
                content['pages'] = pages
            fingerprint = json.dumps(
                [exercise_type, instruction.lower(), content],
                sort_keys=True,
                ensure_ascii=False,
            )
            if fingerprint in fingerprints:
                continue
            fingerprints.add(fingerprint)
            result.append({
                'type': exercise_type,
                'instruction': instruction,
                'content': content,
            })
        return result

    @staticmethod
    def _load_progress():
        if PROGRESS_FILE.exists():
            return json.loads(PROGRESS_FILE.read_text(encoding='utf-8'))
        return {'done': {}}

    @staticmethod
    def _mark_progress(progress, unit_number, status):
        progress.setdefault('done', {})[str(unit_number)] = status
        PROGRESS_FILE.write_text(
            json.dumps(progress, indent=2, ensure_ascii=False),
            encoding='utf-8',
        )

    def _print_status(self, definitions):
        from courses.models import Lesson
        from quiz.models import Exercise

        progress = self._load_progress().get('done', {})
        lessons = Lesson.objects.filter(title__startswith='[Book 2]')
        exercises = Exercise.objects.filter(lesson__in=lessons)
        self.stdout.write(
            f"Progress: {sum(v == 'ok' for v in progress.values())}/{len(definitions)} tayyor, "
            f"{sum(v == 'skipped' for v in progress.values())} skipped. "
            f'Baza: {lessons.count()} dars, {exercises.count()} topshiriq, '
            f"{exercises.filter(type='reading').count()} reading."
        )
