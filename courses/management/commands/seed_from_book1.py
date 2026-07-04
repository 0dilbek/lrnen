"""
Book 1 barcha sahifalarini Gemini orqali o'qib, har bir unit uchun bitta dars yaratadi.
Barcha darslar A1 (Beginner) leveliga biriktiriladi.

Foydalanish:
  # Barchasini tozalab qaytadan yaratish (to'liq jarayon):
  python manage.py seed_from_book1 --clear

  # Faqat ma'lum sahifalar (test uchun):
  python manage.py seed_from_book1 --clear --pages 12-30

  # To'xtatilgan joydan davom ettirish (--clear ishlatmang):
  python manage.py seed_from_book1 --pages 12-176

  # Progress faylini ko'rish:
  python manage.py seed_from_book1 --status
"""
import os
import re
import sys
import time
import json
import base64

from django.core.management.base import BaseCommand
from django.conf import settings
from django.db import transaction


PROGRESS_FILE = os.path.join(settings.BASE_DIR, 'seed_book1_progress.json')
BOOK_IMG_TPL = 'English_for_Everyone_-_Level_1_Beginner_-_Practice_Book_page-{:04d}.jpg'

PROMPT = """You are an expert English language curriculum extractor analyzing a page from "English for Everyone Level 1 Beginner Practice Book".

Extract all exercises from this page as a JSON object.

UNIT DETECTION RULES:
- Look for a unit number in the page header (e.g., "UNIT 21", "Unit 03", "21 Describing a Town").
- Set "unit_number" to the integer unit number (e.g., 21).
- Set "unit_title" to the topic of the unit (e.g., "Describing a Town").
- If no unit number is visible, set "unit_number" to null.

EXERCISE TYPES SUPPORTED:
1. "choose_correct" — cross out the incorrect word, choose the right option.
   content: {"sentences": [{"before": "...", "options": ["A","B"], "after": "...", "correct": 0}]}
2. "fill_blank" — fill in the blanks, complete the sentences.
   content: {"sentences": [{"text": "We ___ Australian.", "answer": "are"}]}
   Note: use ___ (three underscores) as the blank placeholder.
3. "matching" — match left items to right items.
   content: {"left": ["...", "..."], "right": ["...", "..."], "pairs": [0, 1, ...]}
   Where pairs[i] = index in "right" that matches left[i].
4. "listening" — has a headphone icon, track number nearby.
   content: {"questions": [{"question": "...", "options": ["A","B"], "correct": 0}]}
   Set "audio_track" to the track string (e.g., "1.2").

SKIP rules:
- Skip exercises that require a picture/diagram to answer (UNLESS it's a listening exercise).
- Skip vocabulary reference pages, contents pages, answer key pages.

Return ONLY valid JSON in ```json ... ``` blocks:
{
  "unit_number": 21,
  "unit_title": "Describing a Town",
  "exercises": [
    {
      "type": "fill_blank",
      "instruction": "Fill in the gaps with am, is, or are",
      "audio_track": null,
      "is_listening": false,
      "has_linked_image": false,
      "content": {
        "sentences": [{"text": "We ___ Australian.", "answer": "are"}]
      }
    }
  ]
}"""


def encode_image(path):
    with open(path, 'rb') as f:
        return base64.b64encode(f.read()).decode('utf-8')


def find_audio_url(track_str):
    if not track_str:
        return None
    norm = track_str.replace('.', '_').strip()
    parts = norm.split('_')
    if not parts or not parts[0].isdigit():
        return None
    unit_folder = parts[0]
    audio_dir = os.path.join(settings.BASE_DIR, 'static', 'audio', unit_folder)
    if not os.path.exists(audio_dir):
        return None
    candidate = f"{norm}.mp3"
    if os.path.exists(os.path.join(audio_dir, candidate)):
        return f"/static/audio/{unit_folder}/{candidate}"
    for fname in sorted(os.listdir(audio_dir)):
        if fname.lower().startswith(norm.lower()):
            return f"/static/audio/{unit_folder}/{fname}"
    return None


def call_gemini(llm, img_path, page_num):
    from langchain_core.messages import HumanMessage
    filename = os.path.basename(img_path)
    b64 = encode_image(img_path)
    message = HumanMessage(content=[
        {"type": "text", "text": PROMPT},
        {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{b64}"}}
    ])
    for attempt in range(6):
        try:
            response = llm.invoke([message])
            text = response.content.strip()
            if '```json' in text:
                text = text.split('```json')[1].split('```')[0].strip()
            elif '```' in text:
                text = text.split('```')[1].split('```')[0].strip()
            parsed = json.loads(text)
            # Gemini sometimes returns a list instead of a dict — wrap it
            if isinstance(parsed, list):
                parsed = {'exercises': parsed, 'unit_number': None, 'unit_title': ''}
            return parsed
        except Exception as e:
            err = str(e)
            if any(x in err for x in ('429', 'RESOURCE_EXHAUSTED', 'quota', '503', 'UNAVAILABLE', 'overloaded')):
                wait = 30 * (attempt + 1)
                print(f"  ⏳ Server band ({err[:40]}). {wait}s kutilmoqda (urinish {attempt+1}/6)...")
                time.sleep(wait)
            else:
                print(f"  ❌ Xatolik: {e}")
                return None
    return None


class Command(BaseCommand):
    help = 'Book 1 sahifalarini Gemini orqali o\'qib A1 level uchun darslar yaratadi'

    def add_arguments(self, parser):
        parser.add_argument('--clear', action='store_true',
                            help='Boshlashdan oldin barcha [Book 1] darslarni o\'chiradi')
        parser.add_argument('--pages', default='1-176',
                            help='Sahifa oralig\'i, masalan: 12-50  (default: 1-176)')
        parser.add_argument('--status', action='store_true',
                            help='Progress holatini ko\'rsatadi va chiqadi')
        parser.add_argument('--delay', type=float, default=3.0,
                            help='Sahifalar orasidagi kutish (soniya, default: 3)')
        parser.add_argument('--retry-skipped', action='store_true',
                            help='Avval o\'tkazib yuborilgan (skipped) sahifalarni qayta ishlaydi')

    def handle(self, *args, **options):
        from decouple import config as env
        from langchain_google_genai import ChatGoogleGenerativeAI
        from courses.models import Category, Lesson, Level
        from quiz.models import Exercise, Quiz

        # ── Status mode ──
        if options['status']:
            self._print_status()
            return

        # ── API key ──
        api_key = env('GEMINI_API_KRY', default=None) or env('GEMINI_API_KEY', default=None)
        if not api_key:
            self.stderr.write('❌ GEMINI_API_KRY .env faylida topilmadi.')
            return

        llm = ChatGoogleGenerativeAI(
            model=env('GEMINI_MODEL', default='gemini-2.5-flash'),
            google_api_key=api_key,
            temperature=0.1,
        )

        # ── Page range ──
        parts = options['pages'].split('-')
        start_page = int(parts[0])
        end_page = int(parts[1]) if len(parts) > 1 else start_page

        # ── Clear ──
        if options['clear']:
            self._clear_book1(Quiz, Exercise, Lesson)
            # Also reset progress file
            if os.path.exists(PROGRESS_FILE):
                os.remove(PROGRESS_FILE)
                self.stdout.write('  Progress fayli o\'chirildi.')

        # ── Ensure A1 level and category ──
        a1_level, _ = Level.objects.get_or_create(
            slug='a1',
            defaults={'order': 1}
        )
        category, _ = Category.objects.get_or_create(
            name='Book 1 – Beginner',
            defaults={'description': 'DK English for Everyone Level 1 Beginner Practice Book'}
        )

        # ── Load progress ──
        progress = self._load_progress()

        # ── Process pages ──
        self.stdout.write(self.style.SUCCESS(
            f'\n🚀 Sahifalar {start_page}–{end_page} qayta ishlanmoqda...\n'
        ))

        book_dir = os.path.join(settings.BASE_DIR, 'static', 'book')

        retry_skipped = options.get('retry_skipped', False)

        for page_num in range(start_page, end_page + 1):
            prev_status = progress.get('done', {}).get(str(page_num))
            if prev_status == 'ok':
                self.stdout.write(f'  ⏭  Sahifa {page_num:3d} — allaqachon bajarilgan, o\'tkazildi.')
                continue
            if prev_status == 'skipped' and not retry_skipped:
                self.stdout.write(f'  ⏭  Sahifa {page_num:3d} — oldin skipped, o\'tkazildi.')
                continue

            filename = BOOK_IMG_TPL.format(page_num)
            img_path = os.path.join(book_dir, filename)

            if not os.path.exists(img_path):
                self.stdout.write(f'  ⚠️  Sahifa {page_num:3d} — rasm topilmadi ({filename}), o\'tkazildi.')
                self._mark_done(progress, page_num, skipped=True)
                continue

            self.stdout.write(f'  📄 Sahifa {page_num:3d} tahlil qilinmoqda...')
            data = call_gemini(llm, img_path, page_num)

            if not data:
                self.stdout.write(f'  ❌ Sahifa {page_num:3d} — javob olinmadi, o\'tkazildi.')
                self._mark_done(progress, page_num, skipped=True)
                continue

            unit_num = data.get('unit_number')
            unit_title = (data.get('unit_title') or '').strip()
            exercises = data.get('exercises') or []

            if not exercises:
                self.stdout.write(f'  ⚠️  Sahifa {page_num:3d} — topshiriq yo\'q, o\'tkazildi.')
                self._mark_done(progress, page_num, skipped=True)
                continue

            if unit_num is None:
                self.stdout.write(f'  ⚠️  Sahifa {page_num:3d} — unit raqami aniqlanmadi, o\'tkazildi.')
                self._mark_done(progress, page_num, skipped=True)
                continue

            # ── Get or create ONE lesson per unit ──
            lesson_title = f'[Book 1] Unit {unit_num:02d} — {unit_title}' if unit_title else f'[Book 1] Unit {unit_num:02d}'
            prefix = f'[Book 1] Unit {unit_num:02d}'

            existing = Lesson.objects.filter(title__startswith=prefix).first()
            if existing:
                lesson = existing
                lesson_created = False
            else:
                lesson = Lesson.objects.create(
                    title=lesson_title,
                    description=f'DK English for Everyone Level 1, Unit {unit_num}',
                    video_url='https://www.youtube.com/watch?v=dQw4w9WgXcQ',
                    category=category,
                    order=unit_num,
                )
                lesson_created = True

            # Assign A1 level
            lesson.levels.add(a1_level)

            # ── Add exercises to lesson ──
            added = 0
            current_order = Exercise.objects.filter(lesson=lesson).count()

            for ex_data in exercises:
                ex_type = ex_data.get('type')
                if ex_type not in ('choose_correct', 'fill_blank', 'matching', 'listening'):
                    continue

                is_listening = ex_data.get('is_listening', False) or (ex_type == 'listening')
                has_image = ex_data.get('has_linked_image', False)

                if has_image and not is_listening:
                    continue  # rasmga bog'liq oddiy topshiriqni o'tkazib yubor

                content = ex_data.get('content', {})
                audio_url = None

                if is_listening:
                    ex_type = 'listening'
                    track = ex_data.get('audio_track')
                    audio_url = find_audio_url(track)
                    if has_image:
                        content['image_url'] = f'/static/book/{filename}'

                Exercise.objects.create(
                    lesson=lesson,
                    type=ex_type,
                    instruction=ex_data.get('instruction', ''),
                    content=content,
                    has_audio=bool(audio_url),
                    audio_url=audio_url,
                    order=current_order + added + 1,
                )
                added += 1

            status_icon = '🆕' if lesson_created else '➕'
            self.stdout.write(
                f'  {status_icon} Unit {unit_num:02d} ({lesson.title[:50]}) — {added} ta topshiriq qo\'shildi'
            )
            self._mark_done(progress, page_num)

            if page_num < end_page:
                time.sleep(options['delay'])

        # ── Final summary ──
        total_lessons = Lesson.objects.filter(title__startswith='[Book 1]').count()
        total_exercises = Exercise.objects.filter(lesson__title__startswith='[Book 1]').count()
        self.stdout.write(self.style.SUCCESS(
            f'\n✅ Tugadi!\n'
            f'   Jami darslar: {total_lessons}\n'
            f'   Jami topshiriqlar: {total_exercises}\n'
            f'   Barcha darslar A1 leveliga biriktirilgan.'
        ))

    # ── Helpers ──────────────────────────────────────────────────────────────

    def _clear_book1(self, Quiz, Exercise, Lesson):
        self.stdout.write(self.style.WARNING('\n🗑  Barcha [Book 1] darslar o\'chirilmoqda...'))
        with transaction.atomic():
            lessons = Lesson.objects.filter(title__startswith='[Book 1]')
            ids = list(lessons.values_list('id', flat=True))
            Exercise.objects.filter(lesson_id__in=ids).delete()
            Quiz.objects.filter(lesson_id__in=ids).delete()
            count = lessons.count()
            lessons.delete()
        self.stdout.write(self.style.WARNING(f'  {count} ta dars va barcha bog\'liq ma\'lumotlar o\'chirildi.\n'))

    def _load_progress(self):
        if os.path.exists(PROGRESS_FILE):
            with open(PROGRESS_FILE) as f:
                return json.load(f)
        return {'done': {}}

    def _mark_done(self, progress, page_num, skipped=False):
        progress.setdefault('done', {})[str(page_num)] = 'skipped' if skipped else 'ok'
        with open(PROGRESS_FILE, 'w') as f:
            json.dump(progress, f)

    def _print_status(self):
        progress = self._load_progress()
        done = progress.get('done', {})
        ok = [k for k, v in done.items() if v == 'ok']
        skipped = [k for k, v in done.items() if v == 'skipped']
        self.stdout.write(f'Progress fayli: {PROGRESS_FILE}')
        self.stdout.write(f'Bajarilgan: {len(ok)} ta sahifa')
        self.stdout.write(f'O\'tkazilgan: {len(skipped)} ta sahifa')
        remaining = [str(i) for i in range(1, 177) if str(i) not in done]
        self.stdout.write(f'Qolgan: {len(remaining)} ta sahifa')
        if remaining:
            first, last = remaining[0], remaining[-1]
            self.stdout.write(f'Keyingi: --pages {first}-{last}')
