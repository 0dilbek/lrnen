from django.test import TestCase
from django.core.management import call_command
from rest_framework.test import APIClient
from io import StringIO

from accounts.models import User
from courses.models import Category, Lesson, Level
from quiz.models import AdminNotification, Exercise, ExerciseAttempt, Quiz, QuizAttempt
from quiz.serializers import ExerciseSerializer
from quiz.views import _grade_exercise
from courses.management.commands.repair_book1_exercises import (
    has_missing_correct,
    rows_for,
)
from quiz.management.commands.audit_and_repair_exercises import normalize_multi_blank_row


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


class CourseBookInteractiveExerciseTests(TestCase):
    def setUp(self):
        category = Category.objects.create(name='Interactive book')
        self.lesson = Lesson.objects.create(title='Interactive lesson', category=category)

    def test_word_order_ignores_case_spacing_and_final_punctuation(self):
        exercise = Exercise.objects.create(
            lesson=self.lesson,
            type='word_order',
            instruction='Order the words',
            content={
                'items': [
                    {'tokens': ['Example', 'works.'], 'answer': 'Example works.'},
                    {'tokens': ['She', 'is', 'not', 'here.'], 'answer': 'She is not here.'},
                ],
            },
        )

        correct, score = _grade_exercise(exercise, {'answers': ['  she  is NOT here  ']})

        self.assertTrue(correct)
        self.assertEqual(score, 100)

    def test_written_answer_accepts_reviewed_alternative(self):
        exercise = Exercise.objects.create(
            lesson=self.lesson,
            type='written_answer',
            instruction='Correct the sentence',
            content={
                'questions': [
                    {'prompt': 'Example', 'answer': "It isn't late."},
                    {
                        'prompt': 'It are not late.',
                        'answer': "It isn't late.",
                        'alternatives': ['It is not late.'],
                    },
                ],
            },
        )

        correct, score = _grade_exercise(exercise, {'answers': ['It is not late']})

        self.assertTrue(correct)
        self.assertEqual(score, 100)

    def test_structured_types_require_example_and_real_question(self):
        word_order = ExerciseSerializer(data={
            'lesson': self.lesson.id,
            'type': 'word_order',
            'instruction': 'Order',
            'content': {'items': [{'tokens': ['Only', 'one'], 'answer': 'Only one'}]},
        })
        written = ExerciseSerializer(data={
            'lesson': self.lesson.id,
            'type': 'written_answer',
            'instruction': 'Write',
            'content': {'questions': [{'prompt': 'Only one', 'answer': 'Answer'}]},
        })

        self.assertFalse(word_order.is_valid())
        self.assertFalse(written.is_valid())

    def test_fill_blank_requires_one_answer_per_visible_blank(self):
        broken = ExerciseSerializer(data={
            'lesson': self.lesson.id,
            'type': 'fill_blank',
            'instruction': 'Complete',
            'content': {'sentences': [
                {'text': 'If it ___, we ___ home.', 'answer': 'rains, will stay'},
            ]},
        })
        valid = ExerciseSerializer(data={
            'lesson': self.lesson.id,
            'type': 'fill_blank',
            'instruction': 'Complete',
            'content': {'sentences': [
                {'text': 'If it ___, we ___ home.', 'answer': ['rains', 'will stay']},
            ]},
        })

        self.assertFalse(broken.is_valid())
        self.assertTrue(valid.is_valid(), valid.errors)

    def test_matching_example_count_zero_scores_every_pair(self):
        exercise = Exercise.objects.create(
            lesson=self.lesson,
            type='matching',
            instruction='Match',
            content={
                'left': ['one', 'two'],
                'right': ['first', 'second'],
                'pairs': [0, 1],
                'example_count': 0,
            },
        )

        correct, score = _grade_exercise(exercise, {'matches': {'0': 0, '1': 1}})

        self.assertTrue(correct)
        self.assertEqual(score, 100)

    def test_multi_blank_repair_splits_imported_answers(self):
        row = {
            'text': 'If you ___ (cook), I ___ (wash).',
            'answer': 'cook, will wash',
        }

        self.assertTrue(normalize_multi_blank_row(row, 'Fill in the gaps'))
        self.assertEqual(row['answer'], ['cook', 'will wash'])


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


class LockedExerciseMediaTests(TestCase):
    def test_student_cannot_receive_locked_exercise_media(self):
        level = Level.objects.create(slug='a1', order=1)
        category = Category.objects.create(name='Locked course')
        student = User.objects.create_user('locked-media-student', role='student')
        student.levels.add(level)
        first = Lesson.objects.create(title='First', category=category, order=1)
        locked = Lesson.objects.create(title='Locked', category=category, order=2)
        first.levels.add(level)
        locked.levels.add(level)
        Exercise.objects.create(
            lesson=locked,
            type='reading',
            instruction='Locked reading',
            content={
                'pages': [{'url': '/static/book/page-0001.jpg'}],
                'questions': [
                    {'question': 'Example', 'options': ['A', 'B'], 'correct': 0},
                    {'question': 'Question', 'options': ['A', 'B'], 'correct': 1},
                ],
            },
        )
        client = APIClient()
        client.force_authenticate(student)

        response = client.get(f'/api/quiz/exercises/?lesson={locked.id}')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, [])


class QuizLessonUnlockTests(TestCase):
    def setUp(self):
        level = Level.objects.create(slug='a1', order=1)
        category = Category.objects.create(name='Unlock course')
        self.student = User.objects.create_user('unlock-student', role='student')
        self.student.levels.add(level)
        self.first = Lesson.objects.create(title='First lesson', category=category, order=1)
        self.second = Lesson.objects.create(title='Second lesson', category=category, order=2)
        self.first.levels.add(level)
        self.second.levels.add(level)
        level.current_lesson = self.second
        level.save(update_fields=['current_lesson'])
        self.example = Quiz.objects.create(
            lesson=self.first,
            question='Example',
            options=['Correct', 'Wrong'],
            correct_option_index=0,
        )
        self.scored = Quiz.objects.create(
            lesson=self.first,
            question='Scored',
            options=['Wrong', 'Correct'],
            correct_option_index=1,
        )
        self.client = APIClient()
        self.client.force_authenticate(self.student)

    def test_passing_current_quiz_unlocks_and_returns_next_lesson(self):
        locked_response = self.client.get(f'/api/courses/lessons/{self.second.id}/')
        self.assertEqual(locked_response.status_code, 404)

        submit_response = self.client.post('/api/quiz/submit/', {
            'lesson_id': self.first.id,
            'answers': [
                {'quiz_id': self.scored.id, 'selected_index': 1},
            ],
        }, format='json')

        self.assertEqual(submit_response.status_code, 200, submit_response.data)
        self.assertTrue(submit_response.data['completed'])
        self.assertEqual(submit_response.data['next_lesson_id'], self.second.id)
        unlocked_response = self.client.get(f'/api/courses/lessons/{self.second.id}/')
        self.assertEqual(unlocked_response.status_code, 200)

    def test_progress_endpoint_cannot_bypass_the_final_quiz(self):
        response = self.client.post('/api/courses/progress/', {
            'lesson': self.first.id,
            'status': 'completed',
            'score': 100,
        }, format='json')

        self.assertEqual(response.status_code, 400)
        still_locked = self.client.get(f'/api/courses/lessons/{self.second.id}/')
        self.assertEqual(still_locked.status_code, 404)

    def test_locked_lesson_quiz_cannot_be_submitted_directly(self):
        locked_quiz = Quiz.objects.create(
            lesson=self.second,
            question='Locked',
            options=['Yes', 'No'],
            correct_option_index=0,
        )

        response = self.client.post('/api/quiz/submit/', {
            'lesson_id': self.second.id,
            'answers': [{'quiz_id': locked_quiz.id, 'selected_index': 0}],
        }, format='json')

        self.assertEqual(response.status_code, 403)

    def test_incomplete_quiz_is_rejected_without_partial_attempt(self):
        response = self.client.post('/api/quiz/submit/', {
            'lesson_id': self.first.id,
            'answers': [
                {'quiz_id': self.example.id, 'selected_index': 0},
            ],
        }, format='json')

        self.assertEqual(response.status_code, 400, response.data)
        self.assertEqual(response.data['missing_quiz_ids'], [self.scored.id])
        self.assertFalse(QuizAttempt.objects.filter(user=self.student).exists())

    def test_first_successful_completion_creates_one_admin_notification(self):
        payload = {
            'lesson_id': self.first.id,
            'answers': [{'quiz_id': self.scored.id, 'selected_index': 1}],
        }

        first_response = self.client.post('/api/quiz/submit/', payload, format='json')
        second_response = self.client.post('/api/quiz/submit/', payload, format='json')

        self.assertEqual(first_response.status_code, 200)
        self.assertEqual(second_response.status_code, 200)
        notifications = AdminNotification.objects.filter(student=self.student, lesson=self.first)
        self.assertEqual(notifications.count(), 1)
        self.assertFalse(notifications.first().is_read)
        self.assertEqual(notifications.first().score, 100)

    def test_admin_can_list_and_mark_notification_as_read(self):
        self.client.post('/api/quiz/submit/', {
            'lesson_id': self.first.id,
            'answers': [{'quiz_id': self.scored.id, 'selected_index': 1}],
        }, format='json')
        notification = AdminNotification.objects.get(student=self.student, lesson=self.first)
        admin = User.objects.create_user('notification-admin', role='admin')
        self.client.force_authenticate(admin)

        list_response = self.client.get('/api/quiz/notifications/?status=unread')
        mark_response = self.client.patch(
            f'/api/quiz/notifications/{notification.id}/',
            {'is_read': True},
            format='json',
        )

        self.assertEqual(list_response.status_code, 200)
        self.assertEqual(list_response.data['unread_count'], 1)
        self.assertEqual(list_response.data['results'][0]['student'], self.student.id)
        self.assertEqual(mark_response.status_code, 200)
        self.assertTrue(mark_response.data['is_read'])
        notification.refresh_from_db()
        self.assertIsNotNone(notification.read_at)

    def test_failed_quiz_does_not_notify_and_student_cannot_read_admin_inbox(self):
        failed_response = self.client.post('/api/quiz/submit/', {
            'lesson_id': self.first.id,
            'answers': [{'quiz_id': self.scored.id, 'selected_index': 0}],
        }, format='json')
        inbox_response = self.client.get('/api/quiz/notifications/')

        self.assertEqual(failed_response.status_code, 200)
        self.assertFalse(failed_response.data['completed'])
        self.assertFalse(AdminNotification.objects.filter(student=self.student).exists())
        self.assertEqual(inbox_response.status_code, 403)


class ExerciseAttemptSnapshotTests(TestCase):
    def test_submission_saves_question_and_feedback_snapshots(self):
        level = Level.objects.create(slug='a1', order=1)
        category = Category.objects.create(name='Attempt audit')
        student = User.objects.create_user('attempt-student', role='student')
        student.levels.add(level)
        lesson = Lesson.objects.create(title='Attempt lesson', category=category, order=1)
        lesson.levels.add(level)
        exercise = Exercise.objects.create(
            lesson=lesson,
            type='fill_blank',
            instruction='Complete the sentence',
            content={'sentences': [{'text': 'I ___ ready.', 'answer': 'am'}]},
        )
        client = APIClient()
        client.force_authenticate(student)

        response = client.post('/api/quiz/exercises/submit/', {
            'exercise_id': exercise.id,
            'answer': {'answers': ['am']},
        }, format='json')

        self.assertEqual(response.status_code, 200, response.data)
        attempt = ExerciseAttempt.objects.get(user=student, exercise=exercise)
        self.assertEqual(attempt.content_snapshot, exercise.content)
        self.assertEqual(attempt.feedback['correct_answers'], ['am'])


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


class BeginnerRepairDetectionTests(TestCase):
    def test_only_missing_multiple_choice_correct_is_flagged(self):
        category = Category.objects.create(name='Book 1 repair test')
        lesson = Lesson.objects.create(title='[Book 1] Unit 01', category=category)
        broken = Exercise.objects.create(
            lesson=lesson,
            type='listening',
            instruction='Broken',
            content={'questions': [{'question': 'Q', 'options': ['A', 'B'], 'correct': None}]},
        )
        valid = Exercise.objects.create(
            lesson=lesson,
            type='listening',
            instruction='Valid',
            content={'questions': [{'question': 'Q', 'options': ['A', 'B'], 'correct': 0}]},
        )

        self.assertTrue(has_missing_correct(broken))
        self.assertFalse(has_missing_correct(valid))
        self.assertEqual(rows_for(broken), broken.content['questions'])


class LessonQuizGenerationTests(TestCase):
    def test_command_generates_five_valid_quizzes_and_is_idempotent(self):
        category = Category.objects.create(name='Generated quiz book')
        lesson = Lesson.objects.create(title='Generated quiz lesson', category=category)
        Exercise.objects.create(
            lesson=lesson,
            type='fill_blank',
            instruction='Complete the sentences',
            content={
                'word_panel': ['am', 'is', 'are', 'was', 'were'],
                'sentences': [
                    {'text': 'I ___ ready.', 'answer': 'am'},
                    {'text': 'She ___ happy.', 'answer': 'is'},
                    {'text': 'They ___ here.', 'answer': 'are'},
                    {'text': 'He ___ late yesterday.', 'answer': 'was'},
                    {'text': 'We ___ tired yesterday.', 'answer': 'were'},
                ],
            },
        )
        Quiz.objects.create(
            lesson=lesson,
            question='___',
            options=['I am ready.', 'I is ready.'],
            correct_option_index=0,
        )

        call_command('generate_lesson_quizzes', stdout=StringIO())
        call_command('generate_lesson_quizzes', stdout=StringIO())

        quizzes = list(Quiz.objects.filter(lesson=lesson).order_by('id'))
        self.assertEqual(len(quizzes), 5)
        self.assertEqual(len({quiz.question for quiz in quizzes}), 5)
        self.assertNotEqual(quizzes[0].question, '___')
        for quiz in quizzes:
            self.assertGreaterEqual(len(quiz.options), 2)
            self.assertLess(quiz.correct_option_index, len(quiz.options))
