from django.urls import reverse
from rest_framework.test import APITestCase

from courses.models import Level
from .models import User


class AdminStudentManagementTests(APITestCase):
    def setUp(self):
        self.level = Level.objects.create(slug='a1', order=1)

    def test_staff_user_is_treated_as_platform_admin(self):
        staff = User.objects.create_user(
            'staff-admin', role='student', is_staff=True, password='test-pass'
        )
        self.client.force_authenticate(staff)

        response = self.client.post(reverse('student_list'), {
            'username': 'new-student',
            'full_name': 'New Student',
            'password': 'pass1234',
            'level_ids': [self.level.id],
        }, format='json')

        self.assertEqual(response.status_code, 201, response.data)
        self.assertEqual(response.data['role'], 'student')
        self.assertEqual(response.data['levels'][0]['slug'], 'a1')

    def test_student_creation_requires_a_level(self):
        admin = User.objects.create_user('admin-test', role='admin')
        self.client.force_authenticate(admin)

        response = self.client.post(reverse('student_list'), {
            'username': 'no-level',
            'full_name': 'No Level',
            'password': 'pass1234',
            'level_ids': [],
        }, format='json')

        self.assertEqual(response.status_code, 400)
        self.assertIn('level_ids', response.data)

    def test_student_can_change_own_interface_language(self):
        student = User.objects.create_user('language-student', language='kaa')
        self.client.force_authenticate(student)

        response = self.client.put(reverse('me'), {'language': 'uz'}, format='json')

        self.assertEqual(response.status_code, 200, response.data)
        self.assertEqual(response.data['language'], 'uz')
        student.refresh_from_db()
        self.assertEqual(student.language, 'uz')
