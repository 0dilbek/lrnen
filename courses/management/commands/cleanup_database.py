"""
Loyiha bazasini tartibga solish:
  1. DK English takrorlangan unit darslarini birlashtirish
  2. Keraksiz "Answers" darslarini o'chirish
  3. Vocabulary-only darslarni tegishli unitga birlashtirish
  4. Bo'sh kategoriyalarni o'chirish
  5. Kam topshiriqli darslarni lug'at asosida boyitish

Foydalanish:
  python manage.py cleanup_database --dry-run
  python manage.py cleanup_database
  python manage.py cleanup_database --skip-enrich
"""
import random
import re
from django.core.management.base import BaseCommand
from django.db import transaction

UNIT_RE = re.compile(r'[Uu]nit\s+(\d+)', re.IGNORECASE)
JUNK_TITLE_RE = re.compile(r'\banswers?\b', re.IGNORECASE)
VOCAB_ONLY_RE = re.compile(r'\bvocabulary\b', re.IGNORECASE)


def unit_number(title):
    m = UNIT_RE.search(title)
    return int(m.group(1)) if m else None


def lesson_score(lesson):
    """Master dars tanlash: grammatika/topshiriqli dars ustun."""
    ex = lesson.exercises.count()
    qz = lesson.quizzes.count()
    vocab = lesson.vocabulary.count()
    score = ex * 10 + qz * 5 + vocab
    if JUNK_TITLE_RE.search(lesson.title):
        score -= 1000
    if VOCAB_ONLY_RE.search(lesson.title):
        score -= 200
    if ex == 0 and qz == 0 and vocab > 0:
        score -= 150
    return score


def merge_lesson_into(master, duplicate, stats):
    """duplicate darsdagi barcha kontentni master ga ko'chiradi va duplicate ni o'chiradi."""
    from courses.models import Vocabulary, UserProgress
    from quiz.models import Quiz, Exercise, QuizAttempt, ExerciseAttempt

    stats['moved_exercises'] += Exercise.objects.filter(lesson=duplicate).update(lesson=master)
    stats['moved_quizzes'] += Quiz.objects.filter(lesson=duplicate).update(lesson=master)
    stats['moved_vocabulary'] += Vocabulary.objects.filter(lesson=duplicate).update(lesson=master)

    try:
        from comments.models import Comment
        Comment.objects.filter(lesson=duplicate).update(lesson=master)
    except Exception:
        pass

    QuizAttempt.objects.filter(lesson=duplicate).update(lesson=master)
    ExerciseAttempt.objects.filter(lesson=duplicate).update(lesson=master)

    for prog in UserProgress.objects.filter(lesson=duplicate):
        master_prog, created = UserProgress.objects.get_or_create(
            user=prog.user, lesson=master,
            defaults={'score': prog.score, 'status': prog.status},
        )
        if not created and prog.score > master_prog.score:
            master_prog.score = prog.score
            master_prog.status = prog.status
            master_prog.save()
        prog.delete()

    duplicate.delete()
    stats['deleted_lessons'] += 1


def enrich_lesson_from_vocabulary(lesson, stats, dry_run=False):
    """Lug'atdan matching, quiz va choose_correct topshiriqlar yaratadi."""
    from quiz.models import Quiz, Exercise

    vocab = list(lesson.vocabulary.order_by('order', 'id'))
    if len(vocab) < 4:
        return

    existing_ex = lesson.exercises.count()
    existing_qz = lesson.quizzes.count()
    min_ex = 3
    min_qz = 5

    if existing_ex >= min_ex and existing_qz >= min_qz:
        return

    if dry_run:
        stats['would_enrich'] += 1
        return

    order = existing_ex

    # Matching — 8 tadan guruhlab
    if existing_ex < min_ex:
        for i in range(0, len(vocab), 8):
            batch = vocab[i:i + 8]
            if len(batch) < 4:
                continue
            left = [v.word for v in batch]
            right = [v.translation for v in batch]
            indices = list(range(len(right)))
            random.shuffle(indices)
            shuffled_right = [right[j] for j in indices]
            pairs = [indices.index(idx) for idx in range(len(right))]

            order += 1
            Exercise.objects.create(
                lesson=lesson,
                type='matching',
                instruction="Inglizcha so'zlarni o'zbekcha tarjimalari bilan moslashtiring",
                content={'left': left, 'right': shuffled_right, 'pairs': pairs},
                order=order,
            )
            stats['created_exercises'] += 1
            if lesson.exercises.count() >= min_ex:
                break

    # Quiz — tarjima savollari
    other_translations = [v.translation for v in vocab]
    for v in vocab:
        if lesson.quizzes.count() >= min_qz:
            break
        distractors = [t for t in other_translations if t != v.translation]
        if len(distractors) < 3:
            continue
        wrong = random.sample(distractors, 3)
        options = [v.translation] + wrong
        random.shuffle(options)
        correct_idx = options.index(v.translation)

        Quiz.objects.create(
            lesson=lesson,
            question=f"'{v.word}' so'zining o'zbekcha tarjimasi qaysi?",
            options=options,
            correct_option_index=correct_idx,
        )
        stats['created_quizzes'] += 1

    # choose_correct — misol gaplardan
    if lesson.exercises.count() < min_ex + 1:
        candidates = [v for v in vocab if v.example and v.word.lower() in v.example.lower()]
        if len(candidates) >= 3:
            sentences = []
            for v in candidates[:7]:
                example = v.example
                pattern = re.compile(re.escape(v.word), re.IGNORECASE)
                if not pattern.search(example):
                    continue
                others = [c.word for c in vocab if c.word != v.word]
                if len(others) < 1:
                    continue
                distractor = random.choice(others)
                before = pattern.split(example, 1)[0]
                after = pattern.split(example, 1)[1] if pattern.split(example, 1) else ''
                options = [v.word, distractor] if random.random() > 0.5 else [distractor, v.word]
                sentences.append({
                    'before': before,
                    'options': options,
                    'after': after,
                    'correct': options.index(v.word),
                })

            if sentences:
                order += 1
                Exercise.objects.create(
                    lesson=lesson,
                    type='choose_correct',
                    instruction="Har bir gapda to'g'ri so'zni tanlang",
                    content={'sentences': sentences[:5]},
                    order=order,
                )
                stats['created_exercises'] += 1


class Command(BaseCommand):
    help = 'Loyiha bazasini tartibga soladi: takrorlarni birlashtiradi, keraksizlarni o\'chiradi, darslarni boyitadi'

    def add_arguments(self, parser):
        parser.add_argument('--dry-run', action='store_true',
                            help='Faqat ko\'rsatadi, o\'zgartirmaydi')
        parser.add_argument('--skip-enrich', action='store_true',
                            help='Lug\'atdan topshiriq yaratishni o\'tkazib yuboradi')
        parser.add_argument('--category', type=int, default=None,
                            help='Faqat shu kategoriya ID si uchun (masalan 1=DK English, 5=Book 1)')

    def handle(self, *args, **options):
        from courses.models import Category, Lesson, Level

        dry_run = options['dry_run']
        skip_enrich = options['skip_enrich']
        category_id = options['category']

        stats = {
            'deleted_lessons': 0,
            'moved_exercises': 0,
            'moved_quizzes': 0,
            'moved_vocabulary': 0,
            'deleted_categories': 0,
            'created_exercises': 0,
            'created_quizzes': 0,
            'would_enrich': 0,
        }

        if dry_run:
            self.stdout.write(self.style.WARNING('=== DRY RUN — hech narsa o\'zgarmaydi ===\n'))

        # ── 1. Bo'sh kategoriyalarni o'chirish ──────────────────────────────
        self.stdout.write(self.style.HTTP_INFO('\n▸ Bo\'sh kategoriyalar'))
        for cat in Category.objects.all():
            if cat.lessons.count() == 0:
                self.stdout.write(f'  ✗ O\'chiriladi: [{cat.id}] {cat.name}')
                if not dry_run:
                    cat.delete()
                    stats['deleted_categories'] += 1

        # ── 2. DK English takrorlarni birlashtirish ─────────────────────────
        self.stdout.write(self.style.HTTP_INFO('\n▸ DK English — takrorlangan unitlar'))
        dk_cat = Category.objects.filter(name='DK English').first()
        if dk_cat and (category_id is None or category_id == dk_cat.id):
            self._merge_duplicates(dk_cat, stats, dry_run)

        # ── 3. Book 1 takrorlarni birlashtirish (agar bor bo'lsa) ───────────
        book1_cat = Category.objects.filter(name__icontains='Book 1').first()
        if book1_cat and (category_id is None or category_id == book1_cat.id):
            self.stdout.write(self.style.HTTP_INFO(f'\n▸ {book1_cat.name} — takrorlangan unitlar'))
            self._merge_duplicates(book1_cat, stats, dry_run)

        # ── 4. A1 level biriktirish (Book 1) ────────────────────────────────
        if book1_cat and not dry_run:
            a1 = Level.objects.filter(slug='a1').first()
            if a1:
                for lesson in book1_cat.lessons.all():
                    if not lesson.levels.filter(slug='a1').exists():
                        lesson.levels.add(a1)

        # ── 5. Butunlay bo'sh darslarni o'chirish ────────────────────────────
        self.stdout.write(self.style.HTTP_INFO('\n▸ Bo\'sh darslar (kontentsiz)'))
        for lesson in Lesson.objects.all():
            if (lesson.vocabulary.count() == 0 and lesson.exercises.count() == 0
                    and lesson.quizzes.count() == 0):
                self.stdout.write(f'  ✗ O\'chiriladi: [{lesson.id}] {lesson.title}')
                if not dry_run:
                    lesson.delete()
                    stats['deleted_lessons'] += 1

        # ── 6. Darslarni tartibga solish ────────────────────────────────────
        if not dry_run:
            for cat in Category.objects.filter(lessons__isnull=False).distinct():
                lessons = list(cat.lessons.all())
                for lesson in lessons:
                    num = unit_number(lesson.title)
                    if num is not None:
                        lesson.order = num
                        lesson.save(update_fields=['order'])

        # ── 7. Lug'atdan boyitish ───────────────────────────────────────────
        if not skip_enrich:
            self.stdout.write(self.style.HTTP_INFO('\n▸ Darslarni lug\'at asosida boyitish'))
            qs = Lesson.objects.all()
            if category_id:
                qs = qs.filter(category_id=category_id)
            for lesson in qs:
                before_ex = lesson.exercises.count()
                before_qz = lesson.quizzes.count()
                enrich_lesson_from_vocabulary(lesson, stats, dry_run=dry_run)
                if not dry_run:
                    lesson.refresh_from_db()
                    after_ex = lesson.exercises.count()
                    after_qz = lesson.quizzes.count()
                    if after_ex > before_ex or after_qz > before_qz:
                        self.stdout.write(
                            f'  ✔ [{lesson.id}] {lesson.title[:50]}: '
                            f'ex {before_ex}→{after_ex}, quiz {before_qz}→{after_qz}'
                        )
                elif lesson.vocabulary.count() >= 4 and (before_ex < 3 or before_qz < 5):
                    self.stdout.write(f'  ~ Boyitiladi: [{lesson.id}] {lesson.title[:50]}')

        # ── Natija ──────────────────────────────────────────────────────────
        self.stdout.write('')
        if dry_run:
            self.stdout.write(self.style.WARNING('DRY RUN tugadi. Haqiqatda bajarish: python manage.py cleanup_database'))
        else:
            self.stdout.write(self.style.SUCCESS(
                f'✅ Tugadi:\n'
                f'   O\'chirilgan darslar: {stats["deleted_lessons"]}\n'
                f'   O\'chirilgan kategoriyalar: {stats["deleted_categories"]}\n'
                f'   Ko\'chirilgan exercise: {stats["moved_exercises"]}\n'
                f'   Ko\'chirilgan quiz: {stats["moved_quizzes"]}\n'
                f'   Ko\'chirilgan vocabulary: {stats["moved_vocabulary"]}\n'
                f'   Yaratilgan exercise: {stats["created_exercises"]}\n'
                f'   Yaratilgan quiz: {stats["created_quizzes"]}'
            ))

        # Yakuniy statistika
        from quiz.models import Quiz, Exercise
        from courses.models import Vocabulary
        self.stdout.write(self.style.HTTP_INFO(
            f'\n📊 Hozirgi holat: '
            f'{Lesson.objects.count()} dars, '
            f'{Vocabulary.objects.count()} lug\'at, '
            f'{Quiz.objects.count()} quiz, '
            f'{Exercise.objects.count()} exercise'
        ))

    def _merge_duplicates(self, category, stats, dry_run):
        from courses.models import Lesson

        groups = {}
        for lesson in category.lessons.all():
            num = unit_number(lesson.title)
            if num is not None:
                groups.setdefault(num, []).append(lesson)

        # Avval vocabulary-only darslarni grammatika darsiga birlashtirish
        for num in sorted(groups.keys()):
            group = groups[num]
            vocab_only = [l for l in group if VOCAB_ONLY_RE.search(l.title) or (
                l.vocabulary.count() > 0 and l.exercises.count() == 0 and l.quizzes.count() == 0
            )]
            grammar = [l for l in group if l not in vocab_only]
            if not vocab_only or not grammar:
                continue
            master = max(grammar, key=lesson_score)
            for vo in vocab_only:
                if vo.id == master.id:
                    continue
                self.stdout.write(
                    f'  ↪ Vocab → grammar: [{vo.id}] {vo.title} → [{master.id}] {master.title}'
                )
                if not dry_run:
                    with transaction.atomic():
                        merge_lesson_into(master, vo, stats)
            groups[num] = [l for l in grammar]

        # Keyin qolgan takrorlarni birlashtirish
        for num in sorted(groups.keys()):
            group = groups[num]
            if len(group) < 2:
                continue

            # Junk "Answers" darslarni alohida o'chirish
            junk = [l for l in group if JUNK_TITLE_RE.search(l.title)]
            non_junk = [l for l in group if not JUNK_TITLE_RE.search(l.title)]

            if junk:
                for j in junk:
                    self.stdout.write(f'  ✗ JUNK o\'chiriladi: [{j.id}] {j.title}')
                    if not dry_run:
                        if non_junk:
                            merge_lesson_into(non_junk[0], j, stats)
                        else:
                            j.delete()
                            stats['deleted_lessons'] += 1
                group = non_junk

            if len(group) < 2:
                continue

            master = max(group, key=lesson_score)
            duplicates = [l for l in group if l.id != master.id]

            self.stdout.write(
                self.style.SUCCESS(f'\n  Unit {num:02d} — {len(group)} ta → 1 ta')
            )
            self.stdout.write(
                f'    ✔ MASTER [{master.id}] {master.title} '
                f'(ex={master.exercises.count()}, quiz={master.quizzes.count()}, vocab={master.vocabulary.count()})'
            )
            for d in duplicates:
                self.stdout.write(
                    f'    ✗ merge  [{d.id}] {d.title} '
                    f'(ex={d.exercises.count()}, quiz={d.quizzes.count()}, vocab={d.vocabulary.count()})'
                )

            if not dry_run:
                with transaction.atomic():
                    for d in duplicates:
                        merge_lesson_into(master, d, stats)