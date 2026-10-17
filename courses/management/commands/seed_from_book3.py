"""Import Level 3 Intermediate Practice Book into the local production seed DB.

The command analyzes one complete unit at a time so reading passages spanning
several pages stay in one exercise. It is idempotent: rerunning a unit replaces
only that unit's exercises.
"""
import base64
import json
import os
import re
import shutil
import subprocess
import time
from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction


BOOK_PDF = Path(settings.BASE_DIR) / 'English for Everyone Level 3 Intermediate, Practice Book.pdf'
SOURCE_DIR = Path(settings.BASE_DIR) / 'scratch' / 'book3_pages'
STATIC_DIR = Path(settings.BASE_DIR) / 'static' / 'book3'
PROGRESS_FILE = Path(settings.BASE_DIR) / 'seed_book3_progress.json'
STATIC_NAME = 'English_for_Everyone_Level_3_Intermediate_Practice_Book_page-{page:04d}.jpg'

UNIT_STARTS = [
    (12, 'Making conversation'),
    (17, 'Where things are'),
    (20, 'Numbers and statistics'),
    (22, 'Times and dates'),
    (24, 'Contact details'),
    (27, 'Talking about jobs'),
    (30, 'Routine and free time'),
    (34, 'Everyday activities'),
    (38, 'Describing people'),
    (41, 'What I’m wearing'),
    (45, 'Daily routines'),
    (48, 'Separable phrasal verbs'),
    (52, 'Comparing places'),
    (56, 'Likes and dislikes'),
    (60, 'Early years'),
    (64, 'Changing meaning'),
    (67, 'Places I have been'),
    (70, 'Things I have done'),
    (74, 'Activities in progress'),
    (78, 'My talents and skills'),
    (81, 'Activities and their results'),
    (84, 'Everyday problems'),
    (88, 'General and specific things'),
    (93, 'Myself, yourself'),
    (96, 'What things are for'),
    (101, 'Opinions and plans'),
    (104, 'Future arrangements'),
    (108, 'Planning the future'),
    (113, 'Predictions and promises'),
    (116, 'Possibility'),
    (120, 'Obligations'),
    (122, 'Making deductions'),
    (126, 'Polite requests'),
    (128, 'More phrasal verbs'),
    (130, 'Asking for agreement'),
    (135, 'Things that are always true'),
    (138, 'Describing a process'),
    (142, 'Things that might happen'),
    (146, 'Solving problems'),
    (150, 'Planning activities'),
    (154, 'Unlikely situations'),
    (158, 'Giving advice'),
    (162, 'Real and unreal situations'),
    (166, 'Being specific'),
    (170, 'Adding information'),
    (174, 'What was happening when?'),
    (178, 'Setting the scene'),
    (180, 'Interrupted actions'),
    (184, 'Events in the past'),
    (188, 'Before and after'),
    (192, 'First times'),
    (196, 'Telling a story'),
    (200, 'What happened when?'),
    (204, 'What other people said'),
    (208, 'Telling things to people'),
    (212, 'Suggestions and explanations'),
    (216, 'Telling people what to do'),
    (220, 'What other people asked'),
    (224, 'Reporting simple questions'),
    (228, 'Polite questions'),
    (232, 'Wishes and regrets'),
]


def unit_definitions():
    definitions = []
    for index, (start_page, title) in enumerate(UNIT_STARTS):
        end_page = UNIT_STARTS[index + 1][0] - 1 if index + 1 < len(UNIT_STARTS) else 235
        definitions.append({
            'number': index + 1,
            'title': title,
            'start_page': start_page,
            'end_page': end_page,
        })
    return definitions


def parse_range(value, maximum):
    match = re.fullmatch(r'\s*(\d+)(?:-(\d+))?\s*', value or '')
    if not match:
        raise CommandError('Unit oralig‘i 1-10 yoki 7 ko‘rinishida bo‘lishi kerak.')
    start = int(match.group(1))
    end = int(match.group(2) or start)
    if start < 1 or end > maximum or start > end:
        raise CommandError(f'Unit oralig‘i 1-{maximum} ichida bo‘lishi kerak.')
    return start, end


def image_as_data_url(path):
    encoded = base64.b64encode(path.read_bytes()).decode('ascii')
    return f'data:image/jpeg;base64,{encoded}'


def extract_json(text):
    value = text.strip()
    if '```json' in value:
        value = value.split('```json', 1)[1].split('```', 1)[0]
    elif '```' in value:
        value = value.split('```', 1)[1].split('```', 1)[0]
    return json.loads(value.strip())


def page_source_path(page):
    candidates = [
        SOURCE_DIR / f'page-{page}.jpg',
        SOURCE_DIR / f'page-{page:03d}.jpg',
        SOURCE_DIR / f'page-{page:04d}.jpg',
    ]
    return next((path for path in candidates if path.exists()), None)


def prompt_for_unit(unit):
    pages = f"{unit['start_page']}–{unit['end_page']}"
    return f"""You are extracting interactive exercises from the user-provided
English for Everyone Level 3 Intermediate Practice Book.

These images are all pages of Unit {unit['number']}: "{unit['title']}" (book pages {pages}).
Analyze the pages together and return a single JSON object. Preserve the order of exercises.

SUPPORTED TYPES AND EXACT CONTENT SHAPES:
1. choose_correct:
   {{"sentences":[{{"before":"She ","options":["is","are"],"after":" ready.","correct":0}}]}}
2. fill_blank:
   {{"sentences":[{{"text":"She ___ ready.","answer":"is"}}],"word_panel":["is","are"]}}
   Use exactly ___ for every blank. Omit word_panel when the page has no panel.
3. matching:
   {{"left":["left text"],"right":["right text"],"pairs":[0]}}
   pairs[i] is the index in right matching left[i]. Keep at least two pairs.
4. reading: for an email, article, advert, web page, story, or other passage students must read.
   Use either:
   {{"passage_title":"...","questions":[{{"question":"...","options":["..."],"correct":0}}]}}
   or {{"passage_title":"...","sentences":[{{"text":"... ___ ...","answer":"..."}}]}}
   Include every page containing the passage or its questions in source_pages. A reading may span multiple pages;
   keep it as ONE exercise and list all relevant page numbers.

RULES:
- Return only exercises that work in the supported digital formats.
- Skip speaking-only, free-writing, crossword, word-search, diagram-only, and picture-only exercises.
- Skip ALL listening/audio exercises because no Level 3 audio files were supplied.
- Solve every retained item accurately from the page and your English knowledge.
- Every retained exercise must contain at least two answerable items. The UI uses its first item as a solved sample.
- Do not invent text unrelated to the supplied pages.
- source_pages must contain only page numbers between {unit['start_page']} and {unit['end_page']}.
- For ordinary non-reading exercises source_pages may be empty. For reading it is mandatory.
- Instructions should be concise English copied or normalized from the book.

Return ONLY valid JSON, with no commentary:
{{
  "exercises": [
    {{
      "type": "fill_blank",
      "instruction": "Fill in the gaps",
      "source_pages": [],
      "content": {{"sentences": [{{"text": "Example ___", "answer": "answer"}}]}}
    }}
  ]
}}
"""


def add_example_markers(content):
    result = dict(content or {})
    for key in ('sentences', 'questions'):
        rows = result.get(key)
        if isinstance(rows, list) and rows and isinstance(rows[0], dict):
            result[key] = [
                {**row, **({'is_example': True} if index == 0 else {})}
                for index, row in enumerate(rows)
            ]
    return result


def normalize_correct_indices(content):
    result = dict(content)
    for key in ('sentences', 'questions'):
        rows = result.get(key)
        if not isinstance(rows, list):
            continue
        normalized = []
        for row in rows:
            if not isinstance(row, dict):
                continue
            item = dict(row)
            if 'correct' in item:
                try:
                    item['correct'] = int(item['correct'])
                except (TypeError, ValueError):
                    item['correct'] = 0
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
    help = 'Level 3 Practice Book’ni B1+B2 darslari va mashqlariga import qiladi'

    def add_arguments(self, parser):
        parser.add_argument('--clear', action='store_true', help='Mavjud [Book 3] ma’lumotlarini o‘chiradi')
        parser.add_argument('--render', action='store_true', help='PDF sahifalarini tahlil uchun JPG qiladi')
        parser.add_argument('--units', default='1-61', help='Unit oralig‘i, masalan 1-10')
        parser.add_argument('--delay', type=float, default=1.0, help='AI chaqiruvlari orasidagi soniya')
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
            page
            for unit in selected
            for page in range(unit['start_page'], unit['end_page'] + 1)
            if page_source_path(page) is None
        ]
        if missing:
            raise CommandError(
                f'{len(missing)} ta JPG sahifa topilmadi. Avval --render bilan ishga tushiring. '
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

        b1_level, _ = Level.objects.get_or_create(slug='b1', defaults={'order': 3})
        b2_level, _ = Level.objects.get_or_create(slug='b2', defaults={'order': 4})
        category, _ = Category.objects.get_or_create(
            name='Book 3 – Intermediate',
            defaults={'description': 'DK English for Everyone Level 3 Intermediate Practice Book'},
        )

        if options['clear']:
            with transaction.atomic():
                Lesson.objects.filter(title__startswith='[Book 3]').delete()
            if PROGRESS_FILE.exists():
                PROGRESS_FILE.unlink()
            if STATIC_DIR.exists():
                shutil.rmtree(STATIC_DIR)
            self.stdout.write(self.style.WARNING('Mavjud Book 3 darslari va progress tozalandi.'))

        lessons = {}
        for unit in definitions:
            title = f"[Book 3] Unit {unit['number']:02d} — {unit['title']}"
            lesson, _ = Lesson.objects.update_or_create(
                title__startswith=f"[Book 3] Unit {unit['number']:02d}",
                defaults={
                    'title': title,
                    'description': (
                        'DK English for Everyone Level 3 Intermediate Practice Book, '
                        f"Unit {unit['number']}, pages {unit['start_page']}–{unit['end_page']}"
                    ),
                    'video_url': None,
                    'category': category,
                    'order': unit['number'],
                },
            )
            lesson.levels.add(b1_level, b2_level)
            lessons[unit['number']] = lesson

        progress = self._load_progress()
        retry_skipped = options['retry_skipped']

        self.stdout.write(self.style.SUCCESS(
            f"Level 3 unitlari {start_unit}–{end_unit} tahlil qilinmoqda..."
        ))
        for unit in selected:
            key = str(unit['number'])
            previous = progress.get('done', {}).get(key)
            if previous == 'ok' or (previous == 'skipped' and not retry_skipped):
                self.stdout.write(f"  ⏭ Unit {unit['number']:02d} — {previous}")
                continue

            page_paths = [
                page_source_path(page)
                for page in range(unit['start_page'], unit['end_page'] + 1)
            ]
            content = [{'type': 'text', 'text': prompt_for_unit(unit)}]
            content.extend({
                'type': 'image_url',
                'image_url': {'url': image_as_data_url(path)},
            } for path in page_paths)

            self.stdout.write(
                f"  📚 Unit {unit['number']:02d} — {unit['title']} "
                f"({unit['start_page']}–{unit['end_page']})"
            )
            data = self._call_model(model, HumanMessage(content=content))
            if not data:
                self._mark_progress(progress, unit['number'], 'skipped')
                continue

            exercises = self._normalize_exercises(data.get('exercises') or [], unit)
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

            reading_count = sum(item['type'] == 'reading' for item in exercises)
            self.stdout.write(self.style.SUCCESS(
                f"     {len(exercises)} ta topshiriq, {reading_count} ta reading saqlandi"
            ))
            self._mark_progress(progress, unit['number'], 'ok')
            if unit['number'] < end_unit and options['delay'] > 0:
                time.sleep(options['delay'])

        total_lessons = Lesson.objects.filter(title__startswith='[Book 3]').count()
        total_exercises = Exercise.objects.filter(lesson__title__startswith='[Book 3]').count()
        total_reading = Exercise.objects.filter(
            lesson__title__startswith='[Book 3]', type='reading'
        ).count()
        self.stdout.write(self.style.SUCCESS(
            f'Tugadi: {total_lessons} dars, {total_exercises} topshiriq, '
            f'{total_reading} reading. Barchasi B1 va B2 levellariga biriktirildi.'
        ))

    def _render_pages(self):
        SOURCE_DIR.mkdir(parents=True, exist_ok=True)
        self.stdout.write('PDF 12–235-sahifalari JPG formatiga o‘tkazilmoqda...')
        try:
            subprocess.run([
                'pdftoppm', '-f', '12', '-l', '235', '-jpeg', '-r', '130',
                '-jpegopt', 'quality=84,optimize=y', str(BOOK_PDF), str(SOURCE_DIR / 'page'),
            ], check=True)
        except (FileNotFoundError, subprocess.CalledProcessError) as error:
            raise CommandError(f'PDF sahifalarini yaratib bo‘lmadi: {error}') from error

    def _call_model(self, model, message):
        for attempt in range(1, 6):
            try:
                response = model.invoke([message])
                return extract_json(response.content)
            except Exception as error:
                retryable = any(term in str(error).lower() for term in (
                    '429', 'quota', 'resource_exhausted', '503', 'unavailable', 'overloaded',
                ))
                if not retryable or attempt == 5:
                    self.stderr.write(f'     AI xatosi: {error}')
                    return None
                wait = 20 * attempt
                self.stdout.write(f'     Server band, {wait} soniyadan keyin qayta urinish...')
                time.sleep(wait)
        return None

    def _normalize_exercises(self, raw_exercises, unit):
        allowed = {'choose_correct', 'fill_blank', 'matching', 'reading'}
        visual_only_terms = (
            'picture', 'pictures', 'image', 'images', 'flag', 'flags',
            'diagram', 'grid', 'chart', 'map', 'photo', 'photos',
            'illustration', 'illustrations', 'look at the',
        )
        result = []
        seen = set()
        for raw in raw_exercises:
            if not isinstance(raw, dict) or not isinstance(raw.get('content'), dict):
                continue
            exercise_type = raw.get('type')
            instruction = (raw.get('instruction') or '').strip() or 'Complete the exercise'
            if exercise_type != 'reading' and any(
                term in instruction.lower() for term in visual_only_terms
            ):
                continue
            content = normalize_correct_indices(raw.get('content') or {})
            content = add_example_markers(content)
            if exercise_type not in allowed or item_count(exercise_type, content) < 2:
                continue

            if exercise_type == 'matching':
                left = content.get('left') or []
                right = content.get('right') or []
                pairs = content.get('pairs') or []
                if len(right) < 2 or len(pairs) != len(left):
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
                        'url': f'/static/book3/{destination.name}',
                        'page_number': page,
                        'caption': f'Level 3 Practice Book — {page}-sahifa',
                    })
                content['pages'] = pages

            fingerprint = json.dumps(
                [exercise_type, instruction.lower(), content], sort_keys=True, ensure_ascii=False
            )
            if fingerprint in seen:
                continue
            seen.add(fingerprint)
            result.append({
                'type': exercise_type,
                'instruction': instruction,
                'content': content,
            })
        return result

    def _load_progress(self):
        if PROGRESS_FILE.exists():
            return json.loads(PROGRESS_FILE.read_text(encoding='utf-8'))
        return {'done': {}}

    def _mark_progress(self, progress, unit_number, status):
        progress.setdefault('done', {})[str(unit_number)] = status
        PROGRESS_FILE.write_text(
            json.dumps(progress, indent=2, ensure_ascii=False), encoding='utf-8'
        )

    def _print_status(self, definitions):
        from courses.models import Lesson
        from quiz.models import Exercise

        progress = self._load_progress().get('done', {})
        ok = sum(value == 'ok' for value in progress.values())
        skipped = sum(value == 'skipped' for value in progress.values())
        lessons = Lesson.objects.filter(title__startswith='[Book 3]')
        exercises = Exercise.objects.filter(lesson__in=lessons)
        self.stdout.write(
            f'Progress: {ok}/{len(definitions)} unit tayyor, {skipped} ta skipped. '
            f'Bazadagi holat: {lessons.count()} dars, {exercises.count()} topshiriq, '
            f"{exercises.filter(type='reading').count()} reading."
        )
