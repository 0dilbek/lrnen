"""
Usage:
  python manage.py extract_exercises --part 1              # exercises + vocabulary
  python manage.py extract_exercises --all-parts           # barcha 5 ta part
  python manage.py extract_exercises --all-parts --vocab-only  # faqat lug'atlar
  python manage.py extract_exercises --part 1 --dry-run   # API chaqiradi, DB ga saqlamaydi
  python manage.py extract_exercises --part 1 --list-only # API chaqirmaydi, faqat fayllar
  python manage.py extract_exercises --part 1 --start-page 10
"""

import os
import json
import base64
import time
import re
from pathlib import Path

from django.core.management.base import BaseCommand
from django.conf import settings

from courses.models import Lesson, Category, Vocabulary
from quiz.models import Quiz, Exercise

# ── Prompt ──────────────────────────────────────────────────────────────────

SYSTEM_PROMPT = """You are an expert at extracting English language exercises from textbook page images.
Your task is to analyze the page and return a strict JSON response.
Always return valid JSON. No extra text before or after the JSON."""

EXTRACTION_PROMPT = """Analyze this English textbook page image and extract ALL exercises.

Return ONLY a JSON object in this exact format (no markdown, no extra text):

{
  "page_type": "exercise",
  "unit": 1,
  "unit_title": "Talking about yourself",
  "exercises": [
    {
      "exercise_num": "1.1",
      "type": "choose_correct",
      "has_audio": false,
      "instruction": "Cross out the incorrect word in each sentence",
      "items": [
        {"sentence": "Jack am / is 27 years old.", "options": ["am", "is"], "correct_index": 1}
      ]
    }
  ]
}

RULES:
1. page_type must be one of: "exercise", "vocabulary", "cover", "contents", "intro", "skip"
   - "exercise": page with numbered exercises (1.1, 2.3, etc.)
   - "vocabulary": vocabulary list page (e.g. "Vocabulary The body")
   - "cover", "contents", "intro", "skip": non-exercise pages

2. If page_type is "vocabulary", return vocabulary words in this format:
   {"page_type": "vocabulary", "unit": 6, "unit_title": "The body", "words": [
     {"word": "head", "translation": "bosh", "example": "She nodded her head."},
     {"word": "arm", "translation": "qo'l", "example": ""}
   ]}
   Extract ALL words visible on the page with their translations/definitions.
   If translation is not shown, leave it as empty string.

2b. If page_type is NOT "exercise" AND NOT "vocabulary", return: {"page_type": "skip", "unit": null, "exercises": []}

3. For EACH exercise, detect type:
   - "choose_correct": cross out / circle / underline the correct option (2 options given)
   - "fill_blank": fill in the gap/blank with a word or phrase
   - "matching": match left column to right column
   - "speaking": say out loud / speaking exercises (include but mark type)
   - "listening": ONLY if the exercise PRIMARILY requires listening to audio

4. has_audio: true if there is a  or headphone/speaker icon next to the exercise number

5. For "choose_correct" items:
   {"sentence": "Jack am / is 27 years old.", "options": ["am", "is"], "correct_index": 1}
   Extract the CORRECT answer from the answer key shown, or use context clues.
   If answer not visible, still list the options and set correct_index to the likely correct one.

6. For "fill_blank" items:
   {"sentence": "They ___ Australian.", "answer": "are"}
   Use ___ for blanks. Get answers from the answer key shown on page, or sample answers shown.

7. For "matching" pairs:
   {"left": "They go to", "right": "the gym after work."}

8. For "speaking" exercises:
   {"instruction": "full instruction text", "example": "any example shown"}
   Put in content as: {"items": [{"instruction": "...", "example": "..."}]}

9. Extract ALL visible exercises on the page. A page may have 2-6 exercises.

10. Unit number: Look for "01", "02" etc. at top of page or exercise numbers like "1.1" → unit 1.

IMPORTANT: Return ONLY the JSON object. No explanation, no markdown code blocks."""


# ── Helper functions ─────────────────────────────────────────────────────────

def encode_image(image_path: str) -> str:
    with open(image_path, "rb") as f:
        return base64.standard_b64encode(f.read()).decode("utf-8")


def extract_json(text: str) -> dict:
    """Extract JSON from Claude's response, even if wrapped in markdown."""
    text = text.strip()
    # Remove markdown code blocks if present
    if "```" in text:
        match = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", text, re.DOTALL)
        if match:
            text = match.group(1)
    # Find first { to last }
    start = text.find("{")
    end = text.rfind("}") + 1
    if start != -1 and end > start:
        text = text[start:end]
    return json.loads(text)


def save_vocabulary(lesson, words: list, dry_run: bool, stdout) -> int:
    """Save extracted vocabulary words. Returns count saved."""
    if not words:
        return 0
    saved = 0
    base_order = Vocabulary.objects.filter(lesson=lesson).count() * 10 if lesson else 0
    for i, w in enumerate(words):
        word = w.get('word', '').strip()
        translation = w.get('translation', '').strip()
        example = w.get('example', '').strip()
        if not word:
            continue
        tr = translation or "(tarjima yo'q)"
        log = f"    📖 {word} — {tr}"
        stdout.write(log)
        if not dry_run and lesson:
            Vocabulary.objects.get_or_create(
                lesson=lesson,
                word=word,
                defaults={
                    'translation': translation,
                    'example': example,
                    'order': base_order + i * 10,
                }
            )
        saved += 1
    return saved


def get_or_create_lesson(unit_num: int, unit_title: str, category) -> Lesson:
    """Get existing or create new Lesson for a unit."""
    title = f"Unit {unit_num:02d}: {unit_title}"
    lesson, created = Lesson.objects.get_or_create(
        title=title,
        defaults={
            "description": f"DK English for Everyone Level 2 — Unit {unit_num:02d}",
            "video_url": "https://www.youtube.com/watch?v=placeholder",
            "category": category,
            "order": unit_num,
            "difficulty": "easy" if unit_num <= 7 else "medium" if unit_num <= 14 else "hard",
        }
    )
    return lesson, created


def save_exercises(lesson: Lesson, exercises: list, dry_run: bool, stdout) -> int:
    """Save extracted exercises to the database. Returns count saved."""
    saved = 0
    # Starting order: after existing exercises
    base_order = Exercise.objects.filter(lesson=lesson).count() * 10

    for i, ex in enumerate(exercises):
        ex_type = ex.get("type", "fill_blank")
        instruction = ex.get("instruction", "")
        has_audio = ex.get("has_audio", False)
        items = ex.get("items", [])

        if not instruction or not items:
            stdout.write(f"    [WARN]  Skipping empty exercise {ex.get('exercise_num', '?')}")
            continue

        # Build content based on type
        if ex_type == "choose_correct":
            content = {"items": items}
            # Also create Quiz objects for MCQ
            if not dry_run:
                for item in items:
                    opts = item.get("options", [])
                    cidx = item.get("correct_index", 0)
                    sent = item.get("sentence", "")
                    if opts and sent:
                        Quiz.objects.get_or_create(
                            lesson=lesson,
                            question=sent,
                            defaults={
                                "options": opts,
                                "correct_option_index": cidx,
                            }
                        )

        elif ex_type == "fill_blank":
            content = {"items": items}

        elif ex_type == "matching":
            pairs = ex.get("pairs", items)  # support both keys
            content = {"pairs": pairs}

        elif ex_type == "speaking":
            content = {"items": items if items else [{"instruction": instruction}]}

        elif ex_type == "listening":
            content = {"items": items}
            has_audio = True  # always true for listening

        else:
            content = {"items": items}

        ex_num = ex.get("exercise_num", "")
        log = f"    ✓ [{ex_num}] {ex_type} — {instruction[:60]} {'' if has_audio else ''}"
        stdout.write(log)

        if not dry_run:
            Exercise.objects.get_or_create(
                lesson=lesson,
                instruction=instruction,
                defaults={
                    "type": ex_type,
                    "content": content,
                    "has_audio": has_audio,
                    "audio_url": None,
                    "order": base_order + i * 10,
                }
            )
        saved += 1

    return saved


# ── Command ──────────────────────────────────────────────────────────────────

class Command(BaseCommand):
    help = "Extract exercises from pdf_images using Claude Vision and save to DB"

    def add_arguments(self, parser):
        parser.add_argument(
            "--part", type=int, default=None,
            help="Process a specific part (1-5)"
        )
        parser.add_argument(
            "--all-parts", action="store_true",
            help="Process all 5 parts"
        )
        parser.add_argument(
            "--start-page", type=int, default=1,
            help="Start from this page number (1-indexed)"
        )
        parser.add_argument(
            "--end-page", type=int, default=None,
            help="Stop at this page number"
        )
        parser.add_argument(
            "--dry-run", action="store_true",
            help="Analyze but don't save to database"
        )
        parser.add_argument(
            "--list-only", action="store_true",
            help="List files to process without making any API calls (free preview)"
        )
        parser.add_argument(
            "--vocab-only", action="store_true",
            help="Extract only vocabulary pages, skip exercise pages"
        )
        parser.add_argument(
            "--delay", type=float, default=0.5,
            help="Seconds between API calls (default: 0.5)"
        )

    def handle(self, *args, **options):
        from dotenv import load_dotenv
        load_dotenv()

        api_key = os.environ.get("ANTHROPIC_API_KEY")
        if not api_key:
            self.stderr.write("[ERR] ANTHROPIC_API_KEY not found in .env")
            return

        from anthropic import Anthropic
        client = Anthropic(api_key=api_key)

        dry_run = options["dry_run"]
        list_only = options["list_only"]
        vocab_only = options["vocab_only"]
        delay = options["delay"]

        if list_only:
            self.stdout.write("[LIST ONLY] mode - no API calls, no cost\n")
        elif dry_run:
            self.stdout.write("[DRY RUN] mode - API chaqiriladi (kredit sarflanadi), DB ga saqlanmaydi\n")
        if vocab_only:
            self.stdout.write("[VOCAB ONLY] mode - faqat lug'at sahifalari\n")

        # Determine which parts to process
        if options["all_parts"]:
            parts = list(range(1, 6))
        elif options["part"]:
            parts = [options["part"]]
        else:
            self.stderr.write("[ERR] Specify --part N or --all-parts")
            return

        # Get or create default category
        if not dry_run:
            category, _ = Category.objects.get_or_create(
                name="DK English for Everyone",
                defaults={"description": "Level 2 Beginner Practice Book"}
            )
        else:
            category = None

        pdf_images_dir = Path(settings.BASE_DIR) / "pdf_images"
        total_saved = 0
        unit_lessons = {}  # unit_num → Lesson

        for part_num in parts:
            # Find the folder for this part
            part_folders = sorted(pdf_images_dir.glob(f"*part_{part_num}"))
            if not part_folders:
                # Try without leading zero
                part_folders = sorted(pdf_images_dir.glob(f"*part{part_num}*"))
            if not part_folders:
                self.stderr.write(f"[WARN]  No folder found for part {part_num}")
                continue

            part_folder = part_folders[0]
            images = sorted(part_folder.glob("*.jpg")) + sorted(part_folder.glob("*.png"))

            start = options["start_page"] - 1
            end = options["end_page"] if options["end_page"] else len(images)
            images = images[start:end]

            self.stdout.write(f"\n[PART] Part {part_num}: {part_folder.name}")
            self.stdout.write(f"   Pages: {start+1}–{start+len(images)} ({len(images)} total)\n")

            for idx, img_path in enumerate(images, start=start+1):
                self.stdout.write(f"  [{idx:03d}] {img_path.name}")

                if list_only:
                    continue

                try:
                    image_b64 = encode_image(str(img_path))

                    response = client.messages.create(
                        model="claude-haiku-4-5-20251001",
                        max_tokens=4096,
                        system=SYSTEM_PROMPT,
                        messages=[{
                            "role": "user",
                            "content": [
                                {
                                    "type": "image",
                                    "source": {
                                        "type": "base64",
                                        "media_type": "image/jpeg",
                                        "data": image_b64,
                                    },
                                },
                                {"type": "text", "text": EXTRACTION_PROMPT},
                            ],
                        }],
                    )

                    raw = response.content[0].text
                    data = extract_json(raw)

                    page_type = data.get("page_type", "skip")
                    unit_num = data.get("unit")
                    unit_title = data.get("unit_title") or (f"Unit {unit_num}" if unit_num else "")

                    if page_type not in ("exercise", "vocabulary"):
                        self.stdout.write(f"        → {page_type}, skipping")
                        time.sleep(delay)
                        continue

                    if vocab_only and page_type == "exercise":
                        self.stdout.write(f"        → exercise, skipping (vocab-only mode)")
                        time.sleep(delay)
                        continue

                    if not unit_num:
                        self.stdout.write("        → unit number not found, skipping")
                        time.sleep(delay)
                        continue

                    # Get or create lesson (shared for both exercises and vocabulary)
                    if unit_num not in unit_lessons:
                        if not dry_run:
                            lesson, created = get_or_create_lesson(unit_num, unit_title, category)
                            unit_lessons[unit_num] = lesson
                            if created:
                                self.stdout.write(f"        [LESSON] Created lesson: {lesson.title}")
                        else:
                            self.stdout.write(f"        [LESSON] [DRY] Would create: Unit {unit_num:02d}: {unit_title}")
                            lesson = None
                            unit_lessons[unit_num] = None
                    else:
                        lesson = unit_lessons[unit_num]

                    if page_type == "vocabulary":
                        words = data.get("words", [])
                        n = save_vocabulary(lesson, words, dry_run, self.stdout)
                        total_saved += n
                        self.stdout.write(f"        → {len(words)} so'z topildi, {n} saqlandi")
                    else:
                        exercises = data.get("exercises", [])
                        if not exercises:
                            self.stdout.write("        → no exercises found")
                            time.sleep(delay)
                            continue
                        n = save_exercises(lesson, exercises, dry_run, self.stdout)
                        total_saved += n
                        self.stdout.write(f"        → {len(exercises)} exercises extracted, {n} saved")

                except json.JSONDecodeError as e:
                    self.stderr.write(f"        [ERR] JSON parse error: {e}")
                    self.stderr.write(f"           Raw: {raw[:200]}")
                except Exception as e:
                    err_str = str(e)
                    self.stderr.write(f"        [ERR] Error: {e}")
                    if "credit balance is too low" in err_str or "credit_balance" in err_str:
                        self.stderr.write(
                            "\n[FATAL] Anthropic kredit balansi yetarli emas!\n"
                            "  -> console.anthropic.com/settings/billing ga kirib kredit soling.\n"
                            "  -> Keyin bu commandni qayta ishga tushiring.\n"
                        )
                        return

                time.sleep(delay)

        self.stdout.write(f"\n{'='*50}")
        self.stdout.write(f"[OK] Done! Total exercises {'extracted' if dry_run else 'saved'}: {total_saved}")
        self.stdout.write(f"   Lessons found: {len(unit_lessons)} units")
