import json
import tempfile
from io import StringIO
from pathlib import Path

from django.core.management import call_command
from django.core.management.base import CommandError
from django.test import TestCase

from accounts.models import StudentGroup, User
from courses.models import Category, GroupLessonRelease, Lesson, Level, UserProgress, Vocabulary
from quiz.models import Exercise, Quiz
from quiz.serializers import ExerciseSerializer
from quiz.views import _build_feedback, _grade_exercise


class MultipleAnswerBookTests(TestCase):
    def setUp(self):
        self.lesson = Lesson.objects.create(title='Advice')
        self.exercise = Exercise.objects.create(
            lesson=self.lesson, type='listening', instruction='Choose two',
            audio_url='/static/audio/books/level2/course/43/43_9_1.mp3',
            content={'example_count': 0, 'questions': [
                {'question': 'Choose two suggestions', 'options': ['A', 'B', 'C'], 'correct_indices': [0, 2]},
                {'question': 'Choose one', 'options': ['Yes', 'No'], 'correct': 1},
            ]},
        )

    def test_all_selected_answers_must_match_without_partial_credit(self):
        self.assertEqual(_grade_exercise(self.exercise, {'answers': {'0': [2, 0], '1': 1}}), (True, 100))
        self.assertEqual(_grade_exercise(self.exercise, {'answers': {'0': [0], '1': 1}}), (False, 50))
        self.assertEqual(_grade_exercise(self.exercise, {'answers': {'0': [0, 1, 2], '1': 1}}), (False, 50))
        self.assertEqual(_grade_exercise(self.exercise, {'answers': {'0': [0, 0, 2], '1': 1}}), (False, 50))
        self.assertEqual(_build_feedback(self.exercise, {}, False)['correct_indices'], [[0, 2], 1])

    def test_invalid_correct_indices_are_rejected(self):
        payload = {
            'lesson': self.lesson.id, 'type': 'listening', 'instruction': 'Listen',
            'audio_url': self.exercise.audio_url, 'content': self.exercise.content,
        }
        valid = ExerciseSerializer(data=payload)
        self.assertTrue(valid.is_valid(), valid.errors)
        payload['content'] = {'questions': [{'question': 'Q', 'options': ['A', 'B'], 'correct_indices': [0, 2]}]}
        invalid = ExerciseSerializer(data=payload)
        self.assertFalse(invalid.is_valid())

    def test_legacy_choose_correct_questions_shape_is_scored(self):
        self.exercise.type = 'choose_correct'
        self.assertEqual(
            _grade_exercise(self.exercise, {'answers': [[2, 0], 1]}),
            (True, 100),
        )


class BookEnrichmentImportTests(TestCase):
    def setUp(self):
        self.category = Category.objects.create(name='Book 2 – Elementary')
        self.level = Level.objects.create(slug='a2', order=2)
        self.lesson = Lesson.objects.create(title='Original title', description_uz='Generic', category=self.category, order=1)
        self.lesson.levels.add(self.level)
        self.group = StudentGroup.objects.create(name='Preserved group')
        GroupLessonRelease.objects.create(group=self.group, level=self.level, current_lesson=self.lesson)
        self.student = User.objects.create_user('preserved-student', study_group=self.group)
        self.progress = UserProgress.objects.create(user=self.student, lesson=self.lesson, status='completed', score=90)
        self.original_exercise = Exercise.objects.create(
            lesson=self.lesson, type='choose_correct', instruction='Original task',
            content={'sentences': [{'before': 'Old', 'options': ['One', 'Two'], 'correct': 0}]},
        )
        self.quiz = Quiz.objects.create(lesson=self.lesson, question='Original test', options=['A', 'B'], correct_option_index=1)
        self.manifest = {
            'level': 2, 'review_status': 'reviewed', 'lessons': [{
                'lesson_id': self.lesson.id, 'source_unit': 1,
                'description_uz': 'O‘zingiz haqingizda gapirish uchun am, is va are shakllaridan foydalaning. Namuna: I am a teacher.',
                'description_kaa': 'Ózińiz haqqında sóylew ushın am, is hám are túrlerinen paydalanıń. Mısal: I am a teacher.',
                'vocabulary': [{'word': 'teacher', 'translation_uz': 'o‘qituvchi', 'translation_kaa': 'oqıtıwshı'}],
                'exercises': [{
                    'source_key': 'l2.course.1.2', 'type': 'choose_correct',
                    'instruction_uz': 'To‘g‘ri javobni tanlang.', 'instruction_kaa': 'Durıs juwaptı tańlań.',
                    'content': {
                        'example_count': 0,
                        'sentences': [{'before': 'I ___ a teacher.', 'options': ['am', 'is'], 'correct': 0}],
                        'provenance': {'level': 2, 'book': 'course', 'unit': 1, 'activity': '1.2', 'pages': [12]},
                    },
                }],
            }],
        }

    def run_import(self, **kwargs):
        with tempfile.TemporaryDirectory(prefix='book-import-test-') as temp:
            path = Path(temp) / 'manifest.json'
            path.write_text(json.dumps(self.manifest), encoding='utf-8')
            call_command('import_book_enrichment', manifest=[str(path)], stdout=StringIO(), **kwargs)

    def test_import_is_additive_and_idempotent(self):
        self.run_import()
        self.run_import()
        self.assertEqual(Exercise.objects.filter(lesson=self.lesson).count(), 2)
        self.assertEqual(Vocabulary.objects.filter(lesson=self.lesson).count(), 1)
        self.assertTrue(Exercise.objects.filter(pk=self.original_exercise.id, instruction='Original task').exists())
        self.assertTrue(Quiz.objects.filter(pk=self.quiz.id, correct_option_index=1).exists())
        self.assertTrue(UserProgress.objects.filter(pk=self.progress.id, score=90, status='completed').exists())
        self.student.refresh_from_db()
        self.assertEqual(self.student.study_group_id, self.group.id)
        self.assertEqual(GroupLessonRelease.objects.get(group=self.group).current_lesson_id, self.lesson.id)
        self.lesson.refresh_from_db()
        self.assertEqual(self.lesson.title, 'Original title')

    def test_dry_run_leaves_database_unchanged(self):
        self.run_import(dry_run=True)
        self.assertEqual(Vocabulary.objects.count(), 0)
        self.assertEqual(Exercise.objects.count(), 1)
        self.lesson.refresh_from_db()
        self.assertEqual(self.lesson.description_uz, 'Generic')

    def test_missing_asset_rolls_back_all_changes(self):
        self.manifest['lessons'][0]['exercises'][0]['content']['pages'] = [{'url': '/static/coursebooks/missing-page.jpg'}]
        with self.assertRaises(CommandError):
            self.run_import()
        self.assertEqual(Vocabulary.objects.count(), 0)
        self.assertEqual(Exercise.objects.count(), 1)

    def test_unreviewed_content_cannot_be_published(self):
        self.manifest['review_status'] = 'draft'
        with self.assertRaises(CommandError):
            self.run_import()
        self.assertEqual(Vocabulary.objects.count(), 0)
