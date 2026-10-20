import shutil
import tempfile
from io import StringIO
from pathlib import Path
from unittest.mock import patch

from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.management import call_command
from django.test import override_settings
from django.urls import reverse
from rest_framework.test import APITestCase

from accounts.models import User
from .models import Category, Lesson, Level, MediaAsset, UserProgress, Vocabulary
from .management.commands.seed_from_book2 import parse_range, unit_definitions
from quiz.models import Exercise, Quiz


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
                video_url=f'/media/protected/video/lesson-{number}.mp4',
            )
            lesson.levels.add(self.level)
            self.lessons.append(lesson)
        self.level.current_lesson = self.lessons[-1]
        self.level.save(update_fields=['current_lesson'])
        self.client.force_authenticate(self.student)

    def test_list_returns_every_assigned_lesson_with_lock_state(self):
        response = self.client.get(reverse('lesson_list'))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 4)
        self.assertEqual(
            [lesson['is_locked'] for lesson in response.data],
            [False, True, True, True],
        )
        self.assertTrue(response.data[0]['video_url'].startswith('/api/media/access/'))
        self.assertIsNone(response.data[1]['video_url'])

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


class LessonReleaseSettingsTests(APITestCase):
    def setUp(self):
        self.level = Level.objects.create(slug='a1', order=1)
        self.other_level = Level.objects.create(slug='a2', order=2)
        category = Category.objects.create(name='Release course')
        self.lessons = []
        for number in range(1, 4):
            lesson = Lesson.objects.create(
                title=f'Release lesson {number}', category=category, order=number
            )
            lesson.levels.add(self.level)
            self.lessons.append(lesson)
        self.other_lesson = Lesson.objects.create(
            title='Other level lesson', category=category, order=1
        )
        self.other_lesson.levels.add(self.other_level)
        self.student = User.objects.create_user('release-student', role='student')
        self.student.levels.add(self.level)
        self.admin = User.objects.create_user('release-admin', role='admin')

    def test_default_gate_opens_only_first_lesson(self):
        self.client.force_authenticate(self.student)

        response = self.client.get(reverse('lesson_list'))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            [lesson['is_locked'] for lesson in response.data],
            [False, True, True],
        )
        self.assertEqual(
            response.data[1]['locked_reason'],
            'Bu dars administrator tomonidan hali ochilmagan.',
        )

    def test_admin_can_release_next_lesson_for_one_level(self):
        UserProgress.objects.create(
            user=self.student,
            lesson=self.lessons[0],
            status='completed',
            score=100,
        )
        self.client.force_authenticate(self.admin)
        settings_response = self.client.get(reverse('lesson_release_settings'))
        a1 = next(row for row in settings_response.data if row['id'] == self.level.id)
        self.assertEqual(a1['current_lesson_id'], self.lessons[0].id)

        update_response = self.client.patch(
            reverse('lesson_release_settings'),
            {'level_id': self.level.id, 'current_lesson_id': self.lessons[1].id},
            format='json',
        )
        self.assertEqual(update_response.status_code, 200, update_response.data)

        self.client.force_authenticate(self.student)
        lessons_response = self.client.get(reverse('lesson_list'))
        self.assertEqual(
            [lesson['is_locked'] for lesson in lessons_response.data],
            [False, False, True],
        )

    def test_student_cannot_change_release_setting(self):
        self.client.force_authenticate(self.student)
        response = self.client.patch(
            reverse('lesson_release_settings'),
            {'level_id': self.level.id, 'current_lesson_id': self.lessons[1].id},
            format='json',
        )
        self.assertEqual(response.status_code, 403)

    def test_lesson_from_another_level_is_rejected(self):
        self.client.force_authenticate(self.admin)
        response = self.client.patch(
            reverse('lesson_release_settings'),
            {'level_id': self.level.id, 'current_lesson_id': self.other_lesson.id},
            format='json',
        )
        self.assertEqual(response.status_code, 400)


class MultiLevelLessonOrderTests(APITestCase):
    def setUp(self):
        self.a1 = Level.objects.create(slug='a1', order=1)
        self.a2 = Level.objects.create(slug='a2', order=2)
        category_a1 = Category.objects.create(name='A1 book')
        category_a2 = Category.objects.create(name='A2 book')
        self.a1_lessons = []
        self.a2_lessons = []
        for order in (1, 2):
            a1_lesson = Lesson.objects.create(
                title=f'A1 Unit {order}', category=category_a1, order=order
            )
            a2_lesson = Lesson.objects.create(
                title=f'A2 Unit {order}', category=category_a2, order=order
            )
            a1_lesson.levels.add(self.a1)
            a2_lesson.levels.add(self.a2)
            self.a1_lessons.append(a1_lesson)
            self.a2_lessons.append(a2_lesson)
        self.a1.current_lesson = self.a1_lessons[-1]
        self.a2.current_lesson = self.a2_lessons[-1]
        self.a1.save(update_fields=['current_lesson'])
        self.a2.save(update_fields=['current_lesson'])

    def test_lessons_are_ordered_by_level_before_unit_number(self):
        student = User.objects.create_user('multi-level')
        student.levels.add(self.a1, self.a2)
        self.client.force_authenticate(student)

        response = self.client.get(reverse('lesson_list'))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            [row['title'] for row in response.data],
            ['A1 Unit 1', 'A1 Unit 2', 'A2 Unit 1', 'A2 Unit 2'],
        )
        self.assertEqual(
            [row['is_locked'] for row in response.data],
            [False, True, True, True],
        )

    def test_student_without_level_safely_starts_from_a1(self):
        student = User.objects.create_user('legacy-no-level')
        self.client.force_authenticate(student)

        response = self.client.get(reverse('lesson_list'))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            [row['title'] for row in response.data],
            ['A1 Unit 1', 'A1 Unit 2'],
        )


class ProtectedMediaTests(APITestCase):
    def setUp(self):
        self.media_root = tempfile.mkdtemp(prefix='english-lms-media-')
        self.settings_override = override_settings(
            MEDIA_ROOT=self.media_root,
            USE_X_ACCEL_REDIRECT=False,
            PROTECTED_MEDIA_URL_TTL=120,
        )
        self.settings_override.enable()
        self.admin = User.objects.create_user('media-admin', role='admin')
        self.student = User.objects.create_user('media-student', role='student')

    def tearDown(self):
        self.settings_override.disable()
        shutil.rmtree(self.media_root, ignore_errors=True)

    def test_admin_upload_gets_raw_storage_and_signed_preview_urls(self):
        self.client.force_authenticate(self.admin)
        upload = SimpleUploadedFile('lesson.mp3', b'ID3\x04\x00\x00sample', content_type='audio/mpeg')

        response = self.client.post(
            reverse('media_assets'),
            {'kind': 'audio', 'file': upload},
            format='multipart',
        )

        self.assertEqual(response.status_code, 201, response.data)
        self.assertTrue(response.data['url'].startswith('/media/protected/audio/'))
        self.assertTrue(response.data['preview_url'].startswith('/api/media/access/'))
        self.assertEqual(MediaAsset.objects.count(), 1)

        protected_response = self.client.get(response.data['preview_url'])
        self.assertEqual(protected_response.status_code, 200)
        self.assertEqual(protected_response['Cache-Control'], 'private, no-store, max-age=0')

    def test_admin_upload_accepts_generic_browser_content_type(self):
        self.client.force_authenticate(self.admin)
        upload = SimpleUploadedFile(
            'browser-audio.mp3',
            b'ID3\x04\x00\x00sample',
            content_type='application/octet-stream',
        )

        response = self.client.post(
            reverse('media_assets'),
            {'kind': 'audio', 'file': upload},
            format='multipart',
        )

        self.assertEqual(response.status_code, 201, response.data)
        self.assertEqual(MediaAsset.objects.count(), 1)

    def test_invalid_media_signature_is_not_served(self):
        response = self.client.get('/api/media/access/not-a-valid-token/')
        self.assertEqual(response.status_code, 404)

    def test_students_receive_signed_lesson_video_but_admin_receives_raw_path(self):
        category = Category.objects.create(name='Media course')
        Lesson.objects.create(
            title='Local video',
            category=category,
            order=1,
            video_url='/media/protected/video/example.mp4',
        )

        self.client.force_authenticate(self.student)
        student_response = self.client.get(reverse('lesson_list'))
        self.assertTrue(student_response.data[0]['video_url'].startswith('/api/media/access/'))

        self.client.force_authenticate(self.admin)
        admin_response = self.client.get(reverse('lesson_list'))
        self.assertEqual(admin_response.data[0]['video_url'], '/media/protected/video/example.mp4')

    @patch('courses.views.subprocess.run')
    def test_admin_can_cut_and_store_audio_clip(self, run_mock):
        source = Path(self.media_root) / 'source.mp3'
        source.write_bytes(b'ID3 source audio')

        def create_clip(arguments, **kwargs):
            Path(arguments[-1]).write_bytes(b'ID3 generated clip')

        run_mock.side_effect = create_clip
        self.client.force_authenticate(self.admin)
        response = self.client.post(reverse('media_audio_clip'), {
            'source_url': '/media/source.mp3',
            'start_seconds': 2.5,
            'end_seconds': 7,
            'name': 'question-2',
        }, format='json')

        self.assertEqual(response.status_code, 201, response.data)
        self.assertEqual(response.data['kind'], 'audio')
        self.assertTrue(response.data['url'].startswith('/media/protected/audio/'))
        self.assertTrue(MediaAsset.objects.get(pk=response.data['id']).file.storage.exists(
            MediaAsset.objects.get(pk=response.data['id']).file.name
        ))


class ListeningAudioPartsCommandTests(APITestCase):
    def test_existing_coursebook_tracks_are_aligned_with_example_and_questions(self):
        temp_root = tempfile.mkdtemp(prefix='listening-parts-')
        self.addCleanup(lambda: shutil.rmtree(temp_root, ignore_errors=True))
        audio_dir = Path(temp_root) / 'static/audio/8'
        audio_dir.mkdir(parents=True)
        for name in ('8_8__eg.mp3', '8_8_1.mp3', '8_8_2.mp3'):
            (audio_dir / name).write_bytes(b'ID3')
        category = Category.objects.create(name='Audio course')
        lesson = Lesson.objects.create(title='Audio lesson', category=category)
        exercise = Exercise.objects.create(
            lesson=lesson,
            type='listening',
            instruction='Listen',
            audio_url='/static/audio/8/8_8_1.mp3',
            has_audio=True,
            content={'questions': [
                {'question': 'Example', 'options': ['A', 'B'], 'correct': 0, 'is_example': True},
                {'question': 'One', 'options': ['A', 'B'], 'correct': 0},
                {'question': 'Two', 'options': ['A', 'B'], 'correct': 1},
            ]},
        )

        with override_settings(BASE_DIR=Path(temp_root)):
            call_command('attach_listening_audio_parts', stdout=StringIO())

        exercise.refresh_from_db()
        self.assertEqual(exercise.content['audio_urls'], [
            '/static/audio/8/8_8__eg.mp3',
            '/static/audio/8/8_8_1.mp3',
            '/static/audio/8/8_8_2.mp3',
        ])


class LocalizedContentTests(APITestCase):
    def setUp(self):
        self.level = Level.objects.create(slug='a1', order=1)
        self.category = Category.objects.create(name='Localized course')
        self.lesson = Lesson.objects.create(
            title='Legacy title',
            title_kaa='Qaraqalpaqsha sabaq',
            title_uz='O‘zbekcha dars',
            description_kaa='Qaraqalpaqsha túsindirme',
            description_uz='O‘zbekcha tushuntirish',
            video_url='/media/protected/video/legacy.mp4',
            video_url_kaa='/media/protected/video/kaa.mp4',
            video_url_uz=None,
            category=self.category,
            order=1,
        )
        self.lesson.levels.add(self.level)
        self.vocabulary = Vocabulary.objects.create(
            lesson=self.lesson,
            word='beautiful',
            translation='sulıw',
            translation_kaa='sulıw',
            translation_uz='chiroyli',
        )
        self.exercise = Exercise.objects.create(
            lesson=self.lesson,
            type='speaking',
            instruction='Speak',
            instruction_kaa='Sóyleń',
            instruction_uz='Gapiring',
            content={'prompt': 'Introduce yourself'},
        )
        self.student = User.objects.create_user('localized-student', language='kaa')
        self.student.levels.add(self.level)
        self.client.force_authenticate(self.student)

    def test_qaraqalpaq_student_receives_qaraqalpaq_text_and_video(self):
        lesson_response = self.client.get(reverse('lesson_list'))
        vocabulary_response = self.client.get(reverse('vocabulary_list'))
        exercise_response = self.client.get(reverse('exercise_list'))

        self.assertEqual(lesson_response.data[0]['title'], 'Qaraqalpaqsha sabaq')
        self.assertIn('/api/media/access/', lesson_response.data[0]['video_url'])
        self.assertEqual(vocabulary_response.data[0]['translation'], 'sulıw')
        self.assertEqual(exercise_response.data[0]['instruction'], 'Sóyleń')
        self.assertNotIn('translation_uz', vocabulary_response.data[0])
        self.assertNotIn('instruction_uz', exercise_response.data[0])

    def test_uzbek_student_receives_uzbek_text_and_no_video_fallback(self):
        self.student.language = 'uz'
        self.student.save(update_fields=['language'])

        lesson_response = self.client.get(reverse('lesson_list'))
        vocabulary_response = self.client.get(reverse('vocabulary_list'))
        exercise_response = self.client.get(reverse('exercise_list'))

        self.assertEqual(lesson_response.data[0]['title'], 'O‘zbekcha dars')
        self.assertIsNone(lesson_response.data[0]['video_url'])
        self.assertEqual(vocabulary_response.data[0]['translation'], 'chiroyli')
        self.assertEqual(exercise_response.data[0]['instruction'], 'Gapiring')

    def test_admin_receives_both_language_fields(self):
        admin = User.objects.create_user('localized-admin', role='admin')
        self.client.force_authenticate(admin)

        lesson_response = self.client.get(reverse('lesson_list'))
        vocabulary_response = self.client.get(reverse('vocabulary_list'))
        exercise_response = self.client.get(reverse('exercise_list'))

        self.assertEqual(lesson_response.data[0]['title_uz'], 'O‘zbekcha dars')
        self.assertEqual(vocabulary_response.data[0]['translation_uz'], 'chiroyli')
        self.assertEqual(exercise_response.data[0]['instruction_uz'], 'Gapiring')


class AdminContentCrudTests(APITestCase):
    def setUp(self):
        self.admin = User.objects.create_user('content-admin', role='admin')
        self.student = User.objects.create_user('content-student', role='student')
        self.level = Level.objects.create(slug='a1', order=1)
        self.category = Category.objects.create(name='Admin CRUD')
        self.lesson = Lesson.objects.create(
            title='Admin CRUD lesson',
            category=self.category,
            order=1,
        )
        self.lesson.levels.add(self.level)
        self.client.force_authenticate(self.admin)

    def test_admin_can_create_update_and_delete_all_lesson_content(self):
        lesson_response = self.client.post(reverse('lesson_list'), {
            'title': 'Temporary lesson',
            'description': 'CRUD test',
            'category': self.category.id,
            'level_ids': [self.level.id],
            'order': 2,
        }, format='json')
        self.assertEqual(lesson_response.status_code, 201, lesson_response.data)
        lesson_id = lesson_response.data['id']

        vocabulary_response = self.client.post(reverse('vocabulary_list'), {
            'lesson': lesson_id,
            'word': 'open',
            'translation': 'ochiq',
            'example': 'The admin panel is open.',
            'order': 1,
        }, format='json')
        self.assertEqual(vocabulary_response.status_code, 201, vocabulary_response.data)
        vocabulary_id = vocabulary_response.data['id']
        update_vocabulary = self.client.put(
            reverse('vocabulary_detail', kwargs={'pk': vocabulary_id}),
            {'translation': 'ochilgan'},
            format='json',
        )
        self.assertEqual(update_vocabulary.status_code, 200, update_vocabulary.data)

        exercise_response = self.client.post(reverse('exercise_list'), {
            'lesson': lesson_id,
            'type': 'speaking',
            'instruction': 'Speak freely',
            'content': {'prompt': 'Introduce yourself'},
            'has_audio': False,
            'order': 1,
        }, format='json')
        self.assertEqual(exercise_response.status_code, 201, exercise_response.data)
        exercise_id = exercise_response.data['id']
        update_exercise = self.client.put(
            reverse('exercise_detail', kwargs={'pk': exercise_id}),
            {'instruction': 'Introduce yourself clearly'},
            format='json',
        )
        self.assertEqual(update_exercise.status_code, 200, update_exercise.data)

        quiz_response = self.client.post(reverse('quiz_list'), {
            'lesson': lesson_id,
            'question': 'Choose the correct answer',
            'options': ['Correct', 'Wrong'],
            'correct_option_index': 0,
        }, format='json')
        self.assertEqual(quiz_response.status_code, 201, quiz_response.data)
        quiz_id = quiz_response.data['id']
        update_quiz = self.client.put(
            reverse('quiz_detail', kwargs={'pk': quiz_id}),
            {'question': 'Choose the right answer'},
            format='json',
        )
        self.assertEqual(update_quiz.status_code, 200, update_quiz.data)

        self.assertEqual(
            self.client.delete(reverse('vocabulary_detail', kwargs={'pk': vocabulary_id})).status_code,
            204,
        )
        self.assertEqual(
            self.client.delete(reverse('exercise_detail', kwargs={'pk': exercise_id})).status_code,
            204,
        )
        self.assertEqual(
            self.client.delete(reverse('quiz_detail', kwargs={'pk': quiz_id})).status_code,
            204,
        )
        self.assertEqual(
            self.client.delete(reverse('lesson_detail', kwargs={'pk': lesson_id})).status_code,
            204,
        )

    def test_every_supported_admin_flag_gets_platform_admin_access(self):
        users = [
            User.objects.create_user('role-admin', role='admin'),
            User.objects.create_user('staff-admin', role='student', is_staff=True),
            User.objects.create_user('super-admin', role='student', is_superuser=True),
        ]
        for index, user in enumerate(users):
            with self.subTest(user=user.username):
                self.client.force_authenticate(user)
                response = self.client.post(reverse('category_list'), {
                    'name': f'Admin category {index}',
                }, format='json')
                self.assertEqual(response.status_code, 201, response.data)

    def test_student_cannot_mutate_admin_content(self):
        self.client.force_authenticate(self.student)
        response = self.client.post(reverse('vocabulary_list'), {
            'lesson': self.lesson.id,
            'word': 'blocked',
            'translation': 'taqiqlangan',
        }, format='json')
        self.assertEqual(response.status_code, 403)


class Book2ImportDefinitionTests(APITestCase):
    def test_all_49_sections_cover_the_book_in_order(self):
        sections = unit_definitions()

        self.assertEqual(len(sections), 49)
        self.assertEqual(sections[0]['start_page'], 12)
        self.assertEqual(sections[-1]['end_page'], 155)
        self.assertTrue(all(
            current['end_page'] + 1 == following['start_page']
            for current, following in zip(sections, sections[1:])
        ))

    def test_unit_range_parser(self):
        self.assertEqual(parse_range('3-8', 49), (3, 8))
        self.assertEqual(parse_range('12', 49), (12, 12))
