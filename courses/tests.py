from django.urls import reverse
from rest_framework.test import APITestCase

from accounts.models import User
from .models import Category, Lesson, Level, UserProgress


class LessonRoadmapAccessTests(APITestCase):
    def setUp(self):
        self.level = Level.objects.create(slug='a1', order=1)
        self.category = Category.objects.create(name='General English')
        self.student = User.objects.create_user(username='student', password='test-pass')
        self.student.levels.add(self.level)
        self.lessons = []
        for number in range(1, 5):
            lesson = Lesson.objects.create(
                title=f'Unit {number}: Lesson {number}',
                category=self.category,
                order=number,
            )
            lesson.levels.add(self.level)
            self.lessons.append(lesson)
        self.client.force_authenticate(self.student)

    def test_list_returns_every_assigned_lesson_with_lock_state(self):
        response = self.client.get(reverse('lesson_list'))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 4)
        self.assertEqual(
            [lesson['is_locked'] for lesson in response.data],
            [False, True, True, True],
        )

    def test_completing_lesson_unlocks_only_the_next_lesson(self):
        UserProgress.objects.create(
            user=self.student,
            lesson=self.lessons[0],
            status='completed',
            score=100,
        )

        response = self.client.get(reverse('lesson_list'))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            [lesson['is_locked'] for lesson in response.data],
            [False, False, True, True],
        )

    def test_locked_lesson_detail_remains_protected(self):
        response = self.client.get(
            reverse('lesson_detail', kwargs={'pk': self.lessons[2].id})
        )

        self.assertEqual(response.status_code, 404)
