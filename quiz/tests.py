from django.test import TestCase
from django.core.management import call_command
from rest_framework.test import APIClient
from io import StringIO

from accounts.models import User
from courses.models import Category, Lesson
from quiz.models import Exercise
from quiz.serializers import ExerciseSerializer
from quiz.views import _grade_exercise


class ReadingExerciseTests(TestCase):
    def setUp(self):
        category = Category.objects.create(name='Book')
        self.lesson = Lesson.objects.create(title='Reading lesson', category=category)
        self.valid_content = {
            'pages': [
                {'url': '/static/book/page-0001.jpg', 'page_number': 1},
                {'url': '/static/book/page-0002.jpg', 'page_number': 2},
            ],
            'questions': [
                {'question': 'Namuna', 'options': ['A', 'B'], 'correct': 0, 'is_example': True},
                {'question': 'Savol', 'options': ['A', 'B'], 'correct': 1},
            ],
        }

    def test_reading_requires_pages_and_a_real_question(self):
        serializer = ExerciseSerializer(data={
            'lesson': self.lesson.id,
            'type': 'reading',
            'instruction': "Matnni o'qing",
            'content': {'pages': [], 'questions': self.valid_content['questions']},
        })
        self.assertFalse(serializer.is_valid())
        self.assertIn('content', serializer.errors)

    def test_multi_page_reading_is_valid(self):
        serializer = ExerciseSerializer(data={
            'lesson': self.lesson.id,
            'type': 'reading',
            'instruction': "Matnni o'qing",
            'content': self.valid_content,
        })
        self.assertTrue(serializer.is_valid(), serializer.errors)

    def test_reading_example_is_not_scored(self):
        exercise = Exercise.objects.create(
            lesson=self.lesson,
            type='reading',
            instruction='Read',
            content=self.valid_content,
        )
        correct, score = _grade_exercise(exercise, {'answers': {'0': 1}})
        self.assertTrue(correct)
        self.assertEqual(score, 100)


class ExerciseAssetLibraryTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.admin = User.objects.create_user('admin-test', role='admin')
        self.student = User.objects.create_user('student-test', role='student')

    def test_admin_can_browse_book_pages(self):
        self.client.force_authenticate(self.admin)
        response = self.client.get('/api/quiz/assets/?kind=book&q=23')
        self.assertEqual(response.status_code, 200)
        self.assertTrue(any(row['page_number'] == 23 for row in response.data['results']))

    def test_student_cannot_browse_admin_assets(self):
        self.client.force_authenticate(self.student)
        response = self.client.get('/api/quiz/assets/?kind=book')
        self.assertEqual(response.status_code, 403)


class ReadingUpgradeCommandTests(TestCase):
    def test_missing_reading_seed_is_idempotent(self):
        category = Category.objects.create(name='Book 1')
        Lesson.objects.create(title='[Book 1] Unit 08', category=category, order=8)

        call_command('upgrade_reading_exercises', stdout=StringIO())
        call_command('upgrade_reading_exercises', stdout=StringIO())

        readings = Exercise.objects.filter(lesson__order=8, type='reading')
        self.assertEqual(readings.count(), 1)
        self.assertEqual(readings.first().content['pages'][0]['page_number'], 29)
        self.assertTrue(readings.first().content['sentences'][0]['is_example'])
