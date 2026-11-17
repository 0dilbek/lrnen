from django.urls import reverse
from rest_framework.test import APITestCase

from accounts.models import StudentGroup, User
from courses.models import Category, GroupLessonRelease, Lesson, Level, UserProgress, Vocabulary
from quiz.models import Exercise, ExerciseAttempt, Quiz, QuizAttempt


class StudentGroupAccessTests(APITestCase):
    def setUp(self):
        self.level = Level.objects.create(slug='a1', order=1)
        category = Category.objects.create(name='Group curriculum')
        self.lessons = []
        for number in range(1, 17):
            lesson = Lesson.objects.create(
                title=f'Lesson {number}', category=category, order=number,
                video_url=f'/media/group-lesson-{number}.mp4',
            )
            lesson.levels.add(self.level)
            self.lessons.append(lesson)
        self.level.current_lesson = self.lessons[-1]
        self.level.save(update_fields=['current_lesson'])
        self.group_one = StudentGroup.objects.create(name='Group 1')
        self.group_two = StudentGroup.objects.create(name='Group 2')
        GroupLessonRelease.objects.create(
            group=self.group_one, level=self.level, current_lesson=self.lessons[9],
        )
        GroupLessonRelease.objects.create(
            group=self.group_two, level=self.level, current_lesson=self.lessons[14],
        )
        self.first = User.objects.create_user('group-one-student', study_group=self.group_one)
        self.second = User.objects.create_user('group-two-student', study_group=self.group_two)
        self.admin = User.objects.create_user('groups-admin', role='admin')
        for student in (self.first, self.second):
            student.levels.add(self.level)
            UserProgress.objects.bulk_create([
                UserProgress(user=student, lesson=lesson, status='completed', score=90)
                for lesson in self.lessons[:14]
            ])

    def test_students_on_same_level_receive_their_own_group_ceiling(self):
        for student, expected_limit in ((self.first, 10), (self.second, 15)):
            with self.subTest(group=student.study_group.name):
                self.client.force_authenticate(student)
                response = self.client.get(reverse('lesson_list'))
                self.assertEqual(response.status_code, 200, response.data)
                unlocked = [row['id'] for row in response.data if not row['is_locked']]
                self.assertEqual(unlocked, [lesson.id for lesson in self.lessons[:expected_limit]])
                self.assertIsNone(response.data[expected_limit]['video_url'])

    def test_released_lesson_is_visible_for_one_group_and_hidden_for_the_other(self):
        url = reverse('lesson_detail', kwargs={'pk': self.lessons[14].id})
        self.client.force_authenticate(self.first)
        self.assertEqual(self.client.get(url).status_code, 404)
        self.client.force_authenticate(self.second)
        self.assertEqual(self.client.get(url).status_code, 200)

    def test_direct_exercise_and_quiz_submission_cannot_bypass_group_ceiling(self):
        lesson = self.lessons[10]
        exercise = Exercise.objects.create(
            lesson=lesson, type='speaking', instruction='Speak', content={'prompt': 'Hello'},
        )
        quiz = Quiz.objects.create(
            lesson=lesson, question='Choose', options=['Yes', 'No'], correct_option_index=0,
        )
        self.client.force_authenticate(self.first)
        exercise_submit = self.client.post(reverse('exercise_submit'), {
            'exercise_id': exercise.id, 'answer': {'text': 'Hello'},
        }, format='json')
        quiz_submit = self.client.post(reverse('quiz_submit'), {
            'lesson_id': lesson.id,
            'answers': [{'quiz_id': quiz.id, 'selected_index': 0}],
        }, format='json')
        self.assertEqual(exercise_submit.status_code, 403, exercise_submit.data)
        self.assertEqual(quiz_submit.status_code, 403, quiz_submit.data)
        self.assertFalse(ExerciseAttempt.objects.filter(user=self.first).exists())
        self.assertFalse(QuizAttempt.objects.filter(user=self.first).exists())
        exercise_list = self.client.get(reverse('exercise_list'), {'lesson': lesson.id})
        quiz_list = self.client.get(reverse('quiz_list'), {'lesson': lesson.id})
        self.assertEqual(exercise_list.data, [])
        self.assertEqual(quiz_list.data, [])

    def test_unfiltered_vocabulary_list_cannot_bypass_group_ceiling(self):
        allowed = Vocabulary.objects.create(
            lesson=self.lessons[9], word='allowed', translation='ochiq',
        )
        future = Vocabulary.objects.create(
            lesson=self.lessons[10], word='future', translation='kelajak',
        )
        self.client.force_authenticate(self.first)
        response = self.client.get(reverse('vocabulary_list'))
        self.assertEqual(response.status_code, 200, response.data)
        self.assertEqual([row['id'] for row in response.data], [allowed.id])
        direct = self.client.get(reverse('vocabulary_list'), {'lesson': future.lesson_id})
        self.assertEqual(direct.status_code, 403, direct.data)

        self.client.force_authenticate(self.second)
        other_group = self.client.get(reverse('vocabulary_list'))
        self.assertEqual({row['id'] for row in other_group.data}, {allowed.id, future.id})

        self.client.force_authenticate(self.admin)
        admin_response = self.client.get(reverse('vocabulary_list'))
        self.assertEqual({row['id'] for row in admin_response.data}, {allowed.id, future.id})

    def test_group_without_setting_defaults_to_first_lesson_instead_of_global_ceiling(self):
        GroupLessonRelease.objects.filter(group=self.group_one).delete()
        self.client.force_authenticate(self.first)
        response = self.client.get(reverse('lesson_list'))
        self.assertEqual(
            [row['id'] for row in response.data if not row['is_locked']],
            [self.lessons[0].id],
        )

    def test_ungrouped_student_keeps_existing_global_release_rule(self):
        self.first.study_group = None
        self.first.save(update_fields=['study_group'])
        self.client.force_authenticate(self.first)
        response = self.client.get(reverse('lesson_list'))
        self.assertFalse(response.data[14]['is_locked'])
        self.assertTrue(response.data[15]['is_locked'])

    def test_group_setting_updates_independently_of_other_groups_and_levels(self):
        other_level = Level.objects.create(slug='a2', order=2)
        other_lesson = Lesson.objects.create(title='A2 first', order=1)
        other_lesson.levels.add(other_level)
        self.client.force_authenticate(self.admin)
        response = self.client.patch(reverse('lesson_release_settings'), {
            'group_id': self.group_one.id,
            'level_id': self.level.id,
            'current_lesson_id': self.lessons[11].id,
        }, format='json')
        self.assertEqual(response.status_code, 200, response.data)
        settings_response = self.client.get(reverse('lesson_release_settings'), {
            'group_id': self.group_one.id,
        })
        self.assertEqual(settings_response.status_code, 200, settings_response.data)
        by_level = {row['id']: row for row in settings_response.data}
        self.assertEqual(by_level[self.level.id]['current_lesson_id'], self.lessons[11].id)
        self.assertEqual(by_level[other_level.id]['current_lesson_id'], other_lesson.id)
        self.assertEqual(
            GroupLessonRelease.objects.get(group=self.group_two, level=self.level).current_lesson_id,
            self.lessons[14].id,
        )
        self.level.refresh_from_db()
        self.assertEqual(self.level.current_lesson_id, self.lessons[-1].id)

    def test_group_release_rejects_lesson_from_another_level(self):
        other_level = Level.objects.create(slug='a2', order=2)
        other_lesson = Lesson.objects.create(title='A2 first', order=1)
        other_lesson.levels.add(other_level)
        self.client.force_authenticate(self.admin)
        response = self.client.patch(reverse('lesson_release_settings'), {
            'group_id': self.group_one.id,
            'level_id': self.level.id,
            'current_lesson_id': other_lesson.id,
        }, format='json')
        self.assertEqual(response.status_code, 400, response.data)


class StudentGroupManagementTests(APITestCase):
    groups_url = '/api/auth/student-groups/'

    def setUp(self):
        self.level = Level.objects.create(slug='a1', order=1)
        self.admin = User.objects.create_user('group-management-admin', role='admin')
        self.group = StudentGroup.objects.create(name='Existing group')
        self.student = User.objects.create_user('member', study_group=self.group)
        self.student.levels.add(self.level)
        self.other = User.objects.create_user('other-member')
        self.other.levels.add(self.level)
        self.client.force_authenticate(self.admin)

    def test_create_group_with_students_and_transfer_membership(self):
        response = self.client.post(self.groups_url, {
            'name': 'New group', 'student_ids': [self.student.id, self.other.id],
        }, format='json')
        self.assertEqual(response.status_code, 201, response.data)
        self.assertEqual(response.data['student_count'], 2)
        self.assertEqual(set(response.data['student_ids']), {self.student.id, self.other.id})
        self.student.refresh_from_db()
        self.assertEqual(self.student.study_group_id, response.data['id'])
        self.assertEqual(self.group.students.count(), 0)
        self.assertEqual(list(self.student.levels.values_list('id', flat=True)), [self.level.id])

    def test_removing_member_does_not_remove_student_or_progress(self):
        lesson = Lesson.objects.create(title='Completed lesson', order=1)
        progress = UserProgress.objects.create(
            user=self.student, lesson=lesson, status='completed', score=90,
        )
        response = self.client.patch(f'{self.groups_url}{self.group.id}/', {
            'student_ids': [],
        }, format='json')
        self.assertEqual(response.status_code, 200, response.data)
        self.student.refresh_from_db()
        self.assertIsNone(self.student.study_group_id)
        self.assertTrue(UserProgress.objects.filter(pk=progress.id, score=90).exists())

    def test_delete_group_keeps_students_and_progress(self):
        lesson = Lesson.objects.create(title='Completed lesson', order=1)
        progress = UserProgress.objects.create(
            user=self.student, lesson=lesson, status='completed', score=90,
        )
        response = self.client.delete(f'{self.groups_url}{self.group.id}/')
        self.assertEqual(response.status_code, 204, response.data)
        self.student.refresh_from_db()
        self.assertIsNone(self.student.study_group_id)
        self.assertTrue(UserProgress.objects.filter(pk=progress.id).exists())

    def test_admin_can_assign_group_when_creating_and_editing_student(self):
        response = self.client.post(reverse('student_list'), {
            'username': 'new-group-student', 'password': 'pass1234',
            'level_ids': [self.level.id], 'group_id': self.group.id,
        }, format='json')
        self.assertEqual(response.status_code, 201, response.data)
        self.assertEqual(response.data['group']['id'], self.group.id)
        update = self.client.patch(reverse('student_detail', kwargs={'pk': response.data['id']}), {
            'group_id': None,
        }, format='json')
        self.assertEqual(update.status_code, 200, update.data)
        self.assertIsNone(update.data['group'])

    def test_invalid_members_are_rejected_without_changing_group(self):
        response = self.client.patch(f'{self.groups_url}{self.group.id}/', {
            'name': 'Should not be saved', 'student_ids': [self.admin.id],
        }, format='json')
        self.assertEqual(response.status_code, 400, response.data)
        self.group.refresh_from_db()
        self.assertEqual(self.group.name, 'Existing group')

    def test_student_cannot_change_own_group_or_manage_groups(self):
        self.client.force_authenticate(self.student)
        self.assertEqual(self.client.get(self.groups_url).status_code, 403)
        self.assertEqual(self.client.post(self.groups_url, {'name': 'Unauthorized'}).status_code, 403)
        response = self.client.put(reverse('me'), {'group_id': None}, format='json')
        self.assertEqual(response.status_code, 200, response.data)
        self.student.refresh_from_db()
        self.assertEqual(self.student.study_group_id, self.group.id)
        release = self.client.patch(reverse('lesson_release_settings'), {
            'group_id': self.group.id, 'level_id': self.level.id, 'current_lesson_id': 1,
        }, format='json')
        self.assertEqual(release.status_code, 403)
