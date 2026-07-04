"""
Faqat Book 1 – Beginner kategoriyasini qoldirish va to'liq boyitish.

Foydalanish:
  python manage.py focus_book1 --dry-run
  python manage.py focus_book1
  python manage.py focus_book1 --skip-seed
"""
import os
import re
import docx
from django.core.management.base import BaseCommand
from django.db import transaction

from courses.management.commands.cleanup_database import enrich_lesson_from_vocabulary
from courses.book1_bootstrap import BOOK1_BOOTSTRAP

BOOK1_NAME = 'Book 1 – Beginner'
VOCAB_DOCX = 'Beginner vocabulary last one.docx'
UNIT_RE = re.compile(r'[Uu]nit\s+(\d+)', re.IGNORECASE)

# DK English for Everyone Level 1 — to'liq unit ro'yxati
BOOK1_UNIT_TITLES = {
    1: 'Introducing yourself',
    2: 'Saying hello and goodbye',
    3: 'Talking about yourself',
    4: 'Talking about other people',
    5: 'Things you have',
    6: 'Using apostrophes',
    7: 'Whose is it?',
    8: 'Talking about your things',
    9: 'Talking about jobs',
    10: 'Talking about your job',
    11: 'Telling the time',
    12: 'Entertainment',
    13: 'Describing your day',
    14: 'Describing your week',
    15: 'Negatives with "to be"',
    16: 'More negatives',
    17: 'Simple questions',
    18: 'Answering questions',
    19: 'Asking questions',
    20: 'Question words',
    21: 'Talking about your town',
    22: 'Using "a" and "the"',
    23: 'Orders and directions',
    24: 'Joining sentences',
    25: 'Describing places',
    26: 'Prepositions of place',
    27: 'Where is it?',
    28: 'The things I have',
    29: 'What do you have?',
    30: 'How many?',
    31: 'Counting',
    32: 'Measuring',
    33: 'Prices',
    34: 'At the shops',
    35: 'Describing things',
    36: 'Comparatives',
    37: 'Talking about sports',
    38: 'Hobbies and free time',
    39: 'Free time',
    40: 'Likes and dislikes',
    41: 'Preferences',
    42: 'Expressing preference',
    43: 'Can and can\'t',
    44: 'What you can and can\'t do',
    45: 'Describing actions',
    46: 'Describing ability',
    47: 'Studying at school',
    48: 'Studying',
}


def extract_unit_numbers(text):
    """'5-6 VOCABULARY' → [5, 6], '7-VOCABULARY' → [7]"""
    match = re.search(r'(\d+)(?:\.\d+)?(?:\s*-\s*(\d+))?', text)
    if not match:
        return []
    start = int(match.group(1))
    end = int(match.group(2)) if match.group(2) else start
    return list(range(start, end + 1))


def iter_block_items(parent):
    from docx.document import Document
    from docx.oxml.table import CT_Tbl
    from docx.oxml.text.paragraph import CT_P
    from docx.table import Table
    from docx.text.paragraph import Paragraph

    if isinstance(parent, Document):
        parent_elm = parent.element.body
    elif hasattr(parent, '_tc'):
        parent_elm = parent._tc
    else:
        raise ValueError('invalid parent')

    for child in parent_elm.iterchildren():
        if isinstance(child, CT_P):
            yield Paragraph(child, parent)
        elif isinstance(child, CT_Tbl):
            yield Table(child, parent)


class Command(BaseCommand):
    help = 'Faqat Book 1 kategoriyasini qoldiradi va darslarni to\'ldiradi'

    def add_arguments(self, parser):
        parser.add_argument('--dry-run', action='store_true')
        parser.add_argument('--skip-seed', action='store_true',
                            help='Skipped sahifalarni Gemini bilan qayta ishlashni o\'tkazib yuboradi')
        parser.add_argument('--skip-vocab', action='store_true',
                            help='docx lug\'at importini o\'tkazib yuboradi')
        parser.add_argument('--skip-enrich', action='store_true',
                            help='Lug\'atdan quiz/exercise yaratishni o\'tkazib yuboradi')

    def handle(self, *args, **options):
        from django.conf import settings
        from courses.models import Category, Lesson, Level, Vocabulary
        from quiz.models import Quiz, Exercise

        dry_run = options['dry_run']
        stats = {
            'deleted_lessons': 0,
            'deleted_categories': 0,
            'imported_vocab': 0,
            'created_exercises': 0,
            'created_quizzes': 0,
        }

        if dry_run:
            self.stdout.write(self.style.WARNING('=== DRY RUN ===\n'))

        # ── 1. Book 1 kategoriyasini ta'minlash ─────────────────────────────
        book1, _ = Category.objects.get_or_create(
            name=BOOK1_NAME,
            defaults={'description': 'DK English for Everyone Level 1 Beginner Practice Book'},
        )
        a1, _ = Level.objects.get_or_create(slug='a1', defaults={'order': 1})

        # ── 2. Boshqa kategoriyalarni o'chirish ─────────────────────────────
        self.stdout.write(self.style.HTTP_INFO('▸ Boshqa kategoriyalarni o\'chirish'))
        other_lessons = Lesson.objects.exclude(category=book1)
        other_cats = Category.objects.exclude(id=book1.id)

        for l in other_lessons:
            self.stdout.write(
                f'  ✗ Dars: [{l.id}] {l.title} '
                f'(ex={l.exercises.count()}, quiz={l.quizzes.count()}, vocab={l.vocabulary.count()})'
            )
        for c in other_cats:
            self.stdout.write(f'  ✗ Kategoriya: [{c.id}] {c.name}')

        if not dry_run:
            with transaction.atomic():
                count = other_lessons.count()
                other_lessons.delete()
                stats['deleted_lessons'] = count
                stats['deleted_categories'] = other_cats.count()
                other_cats.delete()

        # ── 3. Yetishmayotgan unit darslarini yaratish ───────────────────────
        self.stdout.write(self.style.HTTP_INFO('\n▸ Yetishmayotgan unit darslari'))
        if not dry_run:
            self._ensure_all_units(book1, a1, stats)

        # ── 4. Book 1 darslarini A1 ga biriktirish ──────────────────────────
        if not dry_run:
            for lesson in book1.lessons.all():
                lesson.levels.add(a1)
                # Unit 47 kabi noto'liq sarlavhalarni tuzatish
                m = UNIT_RE.search(lesson.title)
                if m:
                    num = int(m.group(1))
                    expected = f'[Book 1] Unit {num:02d} — {BOOK1_UNIT_TITLES.get(num, "")}'
                    if num in BOOK1_UNIT_TITLES and lesson.title != expected:
                        lesson.title = expected
                        lesson.order = num
                        lesson.save(update_fields=['title', 'order'])

        # ── 5. docx dan lug'at import ───────────────────────────────────────
        if not options['skip_vocab']:
            self.stdout.write(self.style.HTTP_INFO('\n▸ Lug\'at import (docx)'))
            docx_path = os.path.join(settings.BASE_DIR, VOCAB_DOCX)
            if os.path.exists(docx_path):
                stats['imported_vocab'] = self._import_vocabulary(docx_path, book1, dry_run)
            else:
                self.stdout.write(self.style.WARNING(f'  ⚠ {VOCAB_DOCX} topilmadi, o\'tkazildi'))

        # ── 6. Skipped sahifalarni qayta ishlash ────────────────────────────
        if not options['skip_seed'] and not dry_run:
            self.stdout.write(self.style.HTTP_INFO('\n▸ Skipped sahifalarni qayta ishlash (Gemini)'))
            from django.core.management import call_command
            call_command('seed_from_book1', '--retry-skipped', verbosity=1)

        # ── 7. Bo'sh unitlarni bootstrap kontent bilan to'ldirish ─────────────
        if not dry_run:
            self.stdout.write(self.style.HTTP_INFO('\n▸ Bo\'sh unitlarni bootstrap qilish'))
            self._bootstrap_gaps(book1, stats)

        # ── 8. Darslarni boyitish ───────────────────────────────────────────
        if not options['skip_enrich']:
            self.stdout.write(self.style.HTTP_INFO('\n▸ Darslarni lug\'at asosida boyitish'))
            enrich_stats = {
                'created_exercises': 0,
                'created_quizzes': 0,
                'would_enrich': 0,
            }
            for lesson in book1.lessons.all().order_by('order'):
                before_ex = lesson.exercises.count()
                before_qz = lesson.quizzes.count()
                enrich_lesson_from_vocabulary(lesson, enrich_stats, dry_run=dry_run)
                if not dry_run:
                    lesson.refresh_from_db()
                    after_ex = lesson.exercises.count()
                    after_qz = lesson.quizzes.count()
                    if after_ex > before_ex or after_qz > before_qz:
                        self.stdout.write(
                            f'  ✔ U{lesson.order:02d} {lesson.title[:45]}: '
                            f'ex {before_ex}→{after_ex}, quiz {before_qz}→{after_qz}'
                        )
            stats['created_exercises'] = enrich_stats['created_exercises']
            stats['created_quizzes'] = enrich_stats['created_quizzes']

        # ── 9. Exercise-only darslarga quiz yaratish ────────────────────────
        if not options['skip_enrich'] and not dry_run:
            self._enrich_from_exercises(book1, stats)

        # ── 10. Keraksiz bo'sh darslarni o'chirish (48 unitdan tashqari) ────
        self.stdout.write(self.style.HTTP_INFO('\n▸ Keraksiz bo\'sh darslar'))
        for lesson in book1.lessons.all():
            m = UNIT_RE.search(lesson.title)
            unit_num = int(m.group(1)) if m else None
            is_expected = unit_num in BOOK1_UNIT_TITLES
            is_empty = (lesson.vocabulary.count() == 0 and lesson.exercises.count() == 0
                        and lesson.quizzes.count() == 0)
            if is_empty and not is_expected:
                self.stdout.write(f'  ✗ [{lesson.id}] {lesson.title}')
                if not dry_run:
                    lesson.delete()
                    stats['deleted_lessons'] += 1
            elif is_empty and is_expected:
                self.stdout.write(f'  ⏳ [{lesson.id}] Unit {unit_num:02d} — seed kutmoqda')

        # ── Natija ──────────────────────────────────────────────────────────
        self.stdout.write('')
        if dry_run:
            self.stdout.write(self.style.WARNING('DRY RUN tugadi.'))
        else:
            self.stdout.write(self.style.SUCCESS(
                f'✅ Book 1 fokus rejimi tugadi:\n'
                f'   O\'chirilgan darslar: {stats["deleted_lessons"]}\n'
                f'   O\'chirilgan kategoriyalar: {stats["deleted_categories"]}\n'
                f'   Import lug\'at: {stats["imported_vocab"]}\n'
                f'   Yaratilgan exercise: {stats["created_exercises"]}\n'
                f'   Yaratilgan quiz: {stats["created_quizzes"]}'
            ))

        total = book1.lessons.count()
        self.stdout.write(self.style.HTTP_INFO(
            f'\n📊 Book 1: {total} dars, '
            f'{Vocabulary.objects.filter(lesson__category=book1).count()} lug\'at, '
            f'{Quiz.objects.filter(lesson__category=book1).count()} quiz, '
            f'{Exercise.objects.filter(lesson__category=book1).count()} exercise'
        ))
        self._print_gaps(book1)

    def _ensure_all_units(self, book1, a1_level, stats):
        from courses.models import Lesson

        existing = set()
        for lesson in book1.lessons.all():
            m = UNIT_RE.search(lesson.title)
            if m:
                existing.add(int(m.group(1)))

        for num, title in BOOK1_UNIT_TITLES.items():
            if num in existing:
                continue
            lesson = Lesson.objects.create(
                title=f'[Book 1] Unit {num:02d} — {title}',
                description=f'DK English for Everyone Level 1, Unit {num}',
                video_url='',
                category=book1,
                order=num,
            )
            lesson.levels.add(a1_level)
            self.stdout.write(f'  + Yaratildi: Unit {num:02d} — {title}')
            stats['created_lessons'] = stats.get('created_lessons', 0) + 1

    def _import_vocabulary(self, docx_path, book1, dry_run):
        from courses.models import Lesson, Vocabulary

        doc = docx.Document(docx_path)
        vocab_data = {}
        current_units = []
        added = 0

        for item in iter_block_items(doc):
            if isinstance(item, docx.text.paragraph.Paragraph):
                text = item.text.strip()
                if not text:
                    continue
                units = extract_unit_numbers(text)
                if units and len(text) < 80 and 'vocabulary' in text.lower() or (
                    units and re.match(r'^\d', text) and len(text) < 40
                ):
                    current_units = units
                    for u in units:
                        vocab_data.setdefault(u, [])

            elif isinstance(item, docx.table.Table):
                if not current_units:
                    continue
                rows_data = []
                for row in item.rows:
                    cells = [c.text.strip() for c in row.cells]
                    if not cells or not cells[0] or cells[0].lower() in ('word', 'vocabulary', 'english'):
                        continue
                    word = cells[0]
                    example = ''
                    translation = ''
                    if len(cells) == 2:
                        translation = cells[1]
                    elif len(cells) >= 3:
                        example = cells[1]
                        translation = cells[2]
                    if word and translation:
                        rows_data.append((word, translation, example))
                target = current_units[-1]
                vocab_data.setdefault(target, []).extend(rows_data)

        for unit_num, words in sorted(vocab_data.items()):
            if not words:
                continue
            prefix = f'[Book 1] Unit {unit_num:02d}'
            lesson = Lesson.objects.filter(
                category=book1, title__startswith=prefix,
            ).first()
            if not lesson:
                self.stdout.write(f'  ⚠ Unit {unit_num:02d} dars topilmadi, {len(words)} so\'z o\'tkazildi')
                continue

            existing_words = set(
                Vocabulary.objects.filter(lesson=lesson).values_list('word', flat=True)
            )
            new_words = [(w, t, e) for w, t, e in words if w not in existing_words]
            if not new_words:
                continue

            self.stdout.write(f'  + Unit {unit_num:02d}: {len(new_words)} ta yangi so\'z')
            if dry_run:
                added += len(new_words)
                continue

            start_order = Vocabulary.objects.filter(lesson=lesson).count()
            for i, (word, trans, example) in enumerate(new_words):
                Vocabulary.objects.create(
                    lesson=lesson, word=word, translation=trans,
                    example=example, order=start_order + i,
                )
                added += 1

        return added

    def _bootstrap_gaps(self, book1, stats):
        from courses.models import Vocabulary
        from quiz.models import Quiz, Exercise

        for unit_num, data in BOOK1_BOOTSTRAP.items():
            prefix = f'[Book 1] Unit {unit_num:02d}'
            lesson = book1.lessons.filter(title__startswith=prefix).first()
            if not lesson:
                continue

            # Lug'at
            existing_words = set(Vocabulary.objects.filter(lesson=lesson).values_list('word', flat=True))
            start_order = Vocabulary.objects.filter(lesson=lesson).count()
            vocab_added = 0
            for i, (word, trans, example) in enumerate(data.get('vocabulary', [])):
                if word in existing_words:
                    continue
                Vocabulary.objects.create(
                    lesson=lesson, word=word, translation=trans,
                    example=example, order=start_order + vocab_added,
                )
                vocab_added += 1
            if vocab_added:
                self.stdout.write(f'  + U{unit_num:02d} vocab: {vocab_added} so\'z')
                stats['imported_vocab'] += vocab_added

            # Topshiriqlar
            ex_added = 0
            if lesson.exercises.count() == 0 and data.get('exercises'):
                for ex_data in data['exercises']:
                    ex_added += 1
                    Exercise.objects.create(
                        lesson=lesson,
                        type=ex_data['type'],
                        instruction=ex_data['instruction'],
                        content=ex_data['content'],
                        order=ex_added,
                    )
                    stats['created_exercises'] += 1

            qz_added = 0
            if lesson.quizzes.count() < 5 and data.get('quizzes'):
                for q, opts, correct in data['quizzes']:
                    if lesson.quizzes.count() >= 5:
                        break
                    Quiz.objects.create(
                        lesson=lesson, question=q, options=opts,
                        correct_option_index=correct,
                    )
                    qz_added += 1
                    stats['created_quizzes'] += 1

            if vocab_added or ex_added or qz_added:
                self.stdout.write(
                    f'  + U{unit_num:02d} bootstrap: '
                    f'vocab={vocab_added}, ex={ex_added}, quiz={qz_added}'
                )

    def _enrich_from_exercises(self, book1, stats):
        """Lug'at yo'q, lekin choose_correct exercise bor darslarga quiz qo'shadi."""
        import random
        from quiz.models import Quiz, Exercise

        for lesson in book1.lessons.all():
            if lesson.quizzes.count() >= 5:
                continue
            for ex in Exercise.objects.filter(lesson=lesson, type='choose_correct'):
                content = ex.content or {}
                sentences = content.get('sentences') or content.get('items') or content.get('questions') or []
                for s in sentences:
                    if lesson.quizzes.count() >= 5:
                        break
                    if 'options' in s and 'before' in s:
                        q = f"{s.get('before', '')} ___ {s.get('after', '')}".strip()
                        opts = s['options']
                        correct = s.get('correct', s.get('correct_index', 0))
                    elif 'options' in s:
                        q = s.get('question') or s.get('sentence', 'Choose the correct answer')
                        opts = s['options']
                        correct = s.get('correct', s.get('correct_index', 0))
                    else:
                        continue
                    if len(opts) < 2:
                        continue
                    Quiz.objects.create(
                        lesson=lesson,
                        question=q,
                        options=opts,
                        correct_option_index=correct,
                    )
                    stats['created_quizzes'] += 1

    def _print_gaps(self, book1):
        from courses.models import Lesson

        self.stdout.write(self.style.HTTP_INFO('\n📋 Yetishmayotgan unitlar (1–48):'))
        existing = set()
        for l in book1.lessons.all():
            m = UNIT_RE.search(l.title)
            if m:
                existing.add(int(m.group(1)))
        missing = [u for u in range(1, 49) if u not in existing]
        if missing:
            self.stdout.write(f'   Yo\'q: {missing}')
        else:
            self.stdout.write('   Barcha 48 unit mavjud ✓')

        self.stdout.write(self.style.HTTP_INFO('\n📋 To\'ldirish kerak bo\'lgan darslar:'))
        gaps = 0
        for l in book1.lessons.all().order_by('order'):
            issues = []
            if l.exercises.count() < 3:
                issues.append(f'ex={l.exercises.count()}')
            if l.quizzes.count() < 5:
                issues.append(f'quiz={l.quizzes.count()}')
            if l.vocabulary.count() < 5:
                issues.append(f'vocab={l.vocabulary.count()}')
            if issues:
                gaps += 1
                self.stdout.write(f'   U{l.order:02d} [{l.id}] {", ".join(issues)} — {l.title[:50]}')
        if not gaps:
            self.stdout.write('   Hammasi to\'liq ✓')