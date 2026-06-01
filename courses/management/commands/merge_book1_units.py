"""
Bir xil unit raqamli [Book 1] darslarni birlashtirib, bitta darsga o'tkazadi.

Foydalanish:
  # Nima bo'lishini ko'rish (o'zgartirmaydi):
  python manage.py merge_book1_units --dry-run

  # Haqiqatda bajarish:
  python manage.py merge_book1_units

  # Faqat bitta unitni birlashtirish:
  python manage.py merge_book1_units --unit 21
"""
import re
from django.core.management.base import BaseCommand
from django.db import transaction


class Command(BaseCommand):
    help = '[Book 1] darslarini unit raqami bo\'yicha birlashtiradi'

    def add_arguments(self, parser):
        parser.add_argument('--dry-run', action='store_true',
                            help='Faqat ko\'rsatadi, o\'zgartirmaydi')
        parser.add_argument('--unit', type=int, default=None,
                            help='Faqat shu unit raqamini birlashtiradi (masalan --unit 21)')

    def handle(self, *args, **options):
        from courses.models import Lesson, Vocabulary, UserProgress
        from quiz.models import Quiz, Exercise, QuizAttempt, ExerciseAttempt
        from comments.models import Comment

        dry_run = options['dry_run']
        only_unit = options['unit']

        if dry_run:
            self.stdout.write(self.style.WARNING('=== DRY RUN — hech narsa o\'zgarmaydi ===\n'))

        # [Book 1] darslarni unit raqami bo'yicha guruhlash
        lessons = Lesson.objects.filter(title__startswith='[Book 1]').order_by('id')
        groups = {}
        for lesson in lessons:
            m = re.search(r'[Uu]nit\s+(\d+)', lesson.title)
            if m:
                key = int(m.group(1))
                groups.setdefault(key, []).append(lesson)

        if only_unit:
            if only_unit not in groups:
                self.stderr.write(f'Unit {only_unit} topilmadi yoki bitta darsdan iborat.')
                return
            groups = {only_unit: groups[only_unit]}

        total_deleted = 0
        total_moved_exercises = 0
        total_moved_quizzes = 0

        for unit_num in sorted(groups.keys()):
            group = groups[unit_num]
            if len(group) < 2:
                continue  # birlashtirish kerak emas

            # Master: eng ko'p exercises bor dars yoki birinchi ID
            master = max(group, key=lambda l: Exercise.objects.filter(lesson=l).count())
            to_merge = [l for l in group if l.id != master.id]

            e_counts = {l.id: Exercise.objects.filter(lesson=l).count() for l in group}
            q_counts = {l.id: Quiz.objects.filter(lesson=l).count() for l in group}

            self.stdout.write(
                self.style.SUCCESS(f'\n━━━ Unit {unit_num:02d} — {len(group)} ta dars → 1 ta birlashadi ━━━')
            )
            self.stdout.write(
                f'  ✔ MASTER  ID={master.id:4}  E={e_counts[master.id]:3}  Q={q_counts[master.id]:3}  {master.title}'
            )
            for l in to_merge:
                self.stdout.write(
                    f'  ✗ o\'chadi  ID={l.id:4}  E={e_counts[l.id]:3}  Q={q_counts[l.id]:3}  {l.title}'
                )

            move_e = sum(e_counts[l.id] for l in to_merge)
            move_q = sum(q_counts[l.id] for l in to_merge)
            self.stdout.write(
                f'  → Master ga ko\'chadi: {move_e} exercise, {move_q} quiz'
            )

            if dry_run:
                continue

            # Haqiqatda birlashtirish
            with transaction.atomic():
                for lesson in to_merge:
                    Exercise.objects.filter(lesson=lesson).update(lesson=master)
                    Quiz.objects.filter(lesson=lesson).update(lesson=master)
                    Vocabulary.objects.filter(lesson=lesson).update(lesson=master)

                    try:
                        Comment.objects.filter(lesson=lesson).update(lesson=master)
                    except Exception:
                        pass

                    QuizAttempt.objects.filter(lesson=lesson).update(lesson=master)
                    ExerciseAttempt.objects.filter(lesson=lesson).update(lesson=master)

                    # UserProgress: eng yaxshi natijani saqla
                    for prog in UserProgress.objects.filter(lesson=lesson):
                        master_prog, created = UserProgress.objects.get_or_create(
                            user=prog.user, lesson=master,
                            defaults={'score': prog.score, 'status': prog.status}
                        )
                        if not created and prog.score > master_prog.score:
                            master_prog.score = prog.score
                            master_prog.status = prog.status
                            master_prog.save()
                        prog.delete()

                    lesson.delete()

            total_deleted += len(to_merge)
            total_moved_exercises += move_e
            total_moved_quizzes += move_q

        self.stdout.write('')
        if dry_run:
            self.stdout.write(self.style.WARNING(
                'DRY RUN tugadi. Haqiqatda bajarish uchun --dry-run flagini olib tashlang.'
            ))
        else:
            self.stdout.write(self.style.SUCCESS(
                f'✅ Tugadi: {total_deleted} dars o\'chirildi, '
                f'{total_moved_exercises} exercise va {total_moved_quizzes} quiz ko\'chirildi.'
            ))
