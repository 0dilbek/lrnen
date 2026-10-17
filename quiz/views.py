from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions
from django.conf import settings
from django.db import transaction
from django.utils import timezone
from pathlib import Path
import re
from .models import (
    AdminNotification,
    Exercise,
    ExerciseAttempt,
    Quiz,
    QuizAttempt,
    QuizAttemptAnswer,
)
from .serializers import (
    QuizSerializer, QuizStudentSerializer, ExerciseSerializer,
    QuizAttemptSerializer, ExerciseAttemptSerializer, AdminNotificationSerializer,
)
from englishLMS.media_security import protected_media_url
from accounts.permissions import IsPlatformAdmin, is_platform_admin


# ── Quiz CRUD ─────────────────────────────────────────────────────────────────

class QuizListView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        lesson_id = request.query_params.get('lesson')
        qs = Quiz.objects.all().order_by('id')
        if lesson_id:
            qs = qs.filter(lesson_id=lesson_id)
        if is_platform_admin(request.user):
            return Response(QuizSerializer(qs, many=True).data)

        from courses.views import _get_visible_lesson_ids, _student_lessons_queryset
        visible_ids = _get_visible_lesson_ids(
            request.user,
            list(_student_lessons_queryset(request.user)),
        )
        qs = qs.filter(lesson_id__in=visible_ids)

        quizzes = list(qs)
        data = QuizStudentSerializer(quizzes, many=True).data
        # Birinchi savol — namuna (to'g'ri javob ko'rsatiladi)
        if quizzes:
            first_id = quizzes[0].id
            for row, quiz in zip(data, quizzes):
                if quiz.id == first_id:
                    row['is_example'] = True
                    row['correct_option_index'] = quiz.correct_option_index
                else:
                    row['is_example'] = False
        return Response(data)

    def post(self, request):
        if not is_platform_admin(request.user):
            return Response({'detail': 'Forbidden'}, status=403)
        serializer = QuizSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=201)


class QuizDetailView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self, pk):
        try:
            return Quiz.objects.get(pk=pk)
        except Quiz.DoesNotExist:
            return None

    def get(self, request, pk):
        obj = self.get_object(pk)
        if not obj:
            return Response({'detail': 'Not found'}, status=404)
        if is_platform_admin(request.user):
            return Response(QuizSerializer(obj).data)
        from courses.views import _get_visible_lesson_ids, _student_lessons_queryset
        visible_ids = _get_visible_lesson_ids(
            request.user,
            list(_student_lessons_queryset(request.user)),
        )
        if obj.lesson_id not in visible_ids:
            return Response({'detail': 'Not found'}, status=404)
        return Response(QuizStudentSerializer(obj).data)

    def put(self, request, pk):
        if not is_platform_admin(request.user):
            return Response({'detail': 'Forbidden'}, status=403)
        obj = self.get_object(pk)
        if not obj:
            return Response({'detail': 'Not found'}, status=404)
        serializer = QuizSerializer(obj, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    def delete(self, request, pk):
        if not is_platform_admin(request.user):
            return Response({'detail': 'Forbidden'}, status=403)
        obj = self.get_object(pk)
        if not obj:
            return Response({'detail': 'Not found'}, status=404)
        obj.delete()
        return Response(status=204)


# ── Quiz submit ───────────────────────────────────────────────────────────────

class QuizSubmitView(APIView):
    """
    Student submits quiz answers for a lesson.
    Saves a QuizAttempt + one QuizAttemptAnswer per question, updates UserProgress.

    Body:
      { lesson_id: N, answers: [{quiz_id, selected_index}, ...] }
    """
    permission_classes = [permissions.IsAuthenticated]

    @transaction.atomic
    def post(self, request):
        answers = request.data.get('answers', [])
        lesson_id = request.data.get('lesson_id')

        if not isinstance(answers, list) or not answers:
            return Response({'detail': 'answers required'}, status=400)
        if not lesson_id:
            return Response({'detail': 'lesson_id required'}, status=400)

        from courses.models import UserProgress, Lesson
        try:
            lesson = Lesson.objects.get(pk=lesson_id)
        except Lesson.DoesNotExist:
            return Response({'detail': 'Lesson not found'}, status=404)

        if not is_platform_admin(request.user):
            from courses.views import (
                _is_lesson_locked, _lesson_locked_reason, _student_lessons_queryset,
            )
            ordered = list(_student_lessons_queryset(request.user))
            if _is_lesson_locked(request.user, lesson, ordered):
                return Response(
                    {'detail': _lesson_locked_reason(request.user, lesson, ordered)},
                    status=403,
                )

        lesson_quizzes = list(Quiz.objects.filter(lesson=lesson).order_by('id'))
        example_quiz_id = lesson_quizzes[0].id if lesson_quizzes else None
        answers_by_id = {}
        for answer in answers:
            if not isinstance(answer, dict):
                continue
            try:
                quiz_id = int(answer.get('quiz_id'))
                selected_index = int(answer.get('selected_index'))
            except (TypeError, ValueError):
                continue
            answers_by_id[quiz_id] = {
                'quiz_id': quiz_id,
                'selected_index': selected_index,
            }

        missing_quiz_ids = [
            quiz.id for quiz in lesson_quizzes
            if quiz.id != example_quiz_id and quiz.id not in answers_by_id
        ]
        if missing_quiz_ids:
            return Response({
                'detail': 'Barcha test savollariga javob bering.',
                'missing_quiz_ids': missing_quiz_ids,
            }, status=400)

        # Namuna savol yuborilmagan bo'lsa, to'g'ri javob bilan to'ldiramiz
        if example_quiz_id and example_quiz_id not in answers_by_id:
            ex_quiz = lesson_quizzes[0]
            answers_by_id[example_quiz_id] = {
                'quiz_id': example_quiz_id,
                'selected_index': ex_quiz.correct_option_index,
            }

        results = []
        correct_count = 0
        scored_total = 0
        answer_objs = []

        for quiz in lesson_quizzes:
            ans = answers_by_id.get(quiz.id)
            if not ans:
                continue
            selected = ans.get('selected_index')
            is_example = quiz.id == example_quiz_id
            is_correct = quiz.correct_option_index == selected

            if is_example:
                # Namuna ballga kirmaydi, lekin to'g'ri deb yoziladi
                selected = quiz.correct_option_index
                is_correct = True
            else:
                scored_total += 1
                if is_correct:
                    correct_count += 1

            opts = quiz.options if isinstance(quiz.options, list) else []
            results.append({
                'quiz_id': quiz.id,
                'question': quiz.question,
                'options': opts,
                'selected_index': selected,
                'selected_text': opts[selected] if opts and selected is not None and 0 <= selected < len(opts) else None,
                'correct_index': quiz.correct_option_index,
                'correct_text': opts[quiz.correct_option_index] if opts and 0 <= quiz.correct_option_index < len(opts) else None,
                'is_correct': is_correct,
                'is_example': is_example,
            })
            answer_objs.append({
                'quiz': quiz,
                'question_snapshot': quiz.question,
                'options_snapshot': quiz.options,
                'selected_index': selected if selected is not None else -1,
                'correct_index': quiz.correct_option_index,
                'is_correct': is_correct,
            })

        total = scored_total
        score = round((correct_count / total) * 100) if total else 100
        completed = score >= 60

        attempt = QuizAttempt.objects.create(
            user=request.user,
            lesson=lesson,
            score=score,
            correct_count=correct_count,
            total_count=total,
        )
        for a in answer_objs:
            QuizAttemptAnswer.objects.create(attempt=attempt, **a)

        progress, _ = UserProgress.objects.get_or_create(user=request.user, lesson=lesson)
        was_completed = progress.status == 'completed'
        if completed:
            progress.status = 'completed'
            progress.score = max(score, progress.score or 0)
        elif progress.status != 'completed':
            progress.status = 'in-progress'
            progress.score = max(score, progress.score or 0)
        progress.save()

        if completed and not was_completed and not is_platform_admin(request.user):
            AdminNotification.objects.get_or_create(
                student=request.user,
                lesson=lesson,
                event_type=AdminNotification.EVENT_LESSON_COMPLETED,
                defaults={
                    'lesson_title_snapshot': lesson.title,
                    'quiz_attempt': attempt,
                    'score': score,
                },
            )

        from courses.views import _get_next_lesson, _is_lesson_locked
        next_lesson = _get_next_lesson(request.user, lesson) if completed else None
        if next_lesson and _is_lesson_locked(request.user, next_lesson):
            next_lesson = None

        return Response({
            'attempt_id': attempt.id,
            'score': score,
            'correct': correct_count,
            'total': total,
            'completed': completed,
            'results': results,
            'next_lesson_id': next_lesson.id if next_lesson else None,
            'next_lesson_title': next_lesson.localized_title(request.user.language) if next_lesson else None,
        })


# ── Exercise CRUD ─────────────────────────────────────────────────────────────

class ExerciseListView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        lesson_id = request.query_params.get('lesson')
        qs = Exercise.objects.all()
        if not is_platform_admin(request.user):
            from courses.views import _get_visible_lesson_ids, _student_lessons_queryset
            visible_ids = _get_visible_lesson_ids(
                request.user,
                list(_student_lessons_queryset(request.user)),
            )
            qs = qs.filter(lesson_id__in=visible_ids)
        if lesson_id:
            qs = qs.filter(lesson_id=lesson_id)
        return Response(ExerciseSerializer(qs, many=True, context={'request': request}).data)

    def post(self, request):
        if not is_platform_admin(request.user):
            return Response({'detail': 'Forbidden'}, status=403)
        serializer = ExerciseSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=201)


class ExerciseDetailView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self, pk):
        try:
            return Exercise.objects.get(pk=pk)
        except Exercise.DoesNotExist:
            return None

    def put(self, request, pk):
        if not is_platform_admin(request.user):
            return Response({'detail': 'Forbidden'}, status=403)
        obj = self.get_object(pk)
        if not obj:
            return Response({'detail': 'Not found'}, status=404)
        serializer = ExerciseSerializer(
            obj, data=request.data, partial=True, context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    def delete(self, request, pk):
        if not is_platform_admin(request.user):
            return Response({'detail': 'Forbidden'}, status=403)
        obj = self.get_object(pk)
        if not obj:
            return Response({'detail': 'Not found'}, status=404)
        obj.delete()
        return Response(status=204)


class ExerciseAssetLibraryView(APIView):
    """Read-only local book/audio browser used by the structured admin editor."""
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        if not is_platform_admin(request.user):
            return Response({'detail': 'Forbidden'}, status=403)

        kind = request.query_params.get('kind', 'book')
        query = request.query_params.get('q', '').strip().lower()
        if kind == 'book':
            return Response(self._book_pages(query))
        if kind == 'audio':
            return Response(self._audio_files(query, request.query_params.get('unit')))
        return Response({'detail': 'kind must be book or audio'}, status=400)

    @staticmethod
    def _book_pages(query):
        rows = []
        for folder in ('book', 'book2', 'book3'):
            book_dir = Path(settings.BASE_DIR) / 'static' / folder
            for path in sorted(book_dir.glob('*.jpg')):
                match = re.search(r'page-(\d+)\.jpg$', path.name, re.IGNORECASE)
                if not match:
                    continue
                page_number = int(match.group(1))
                if query and query not in str(page_number) and query not in path.name.lower():
                    continue
                raw_url = f'/static/{folder}/{path.name}'
                rows.append({
                    'name': path.name,
                    'book': folder,
                    'page_number': page_number,
                    'url': raw_url,
                    'preview_url': protected_media_url(raw_url),
                })
        return {'kind': 'book', 'count': len(rows), 'results': rows}

    @staticmethod
    def _audio_files(query, unit):
        audio_dir = Path(settings.BASE_DIR) / 'static' / 'audio'
        unit_value = str(unit or '').strip()
        search_root = audio_dir / unit_value if unit_value and unit_value.isdigit() else audio_dir
        if not search_root.exists():
            return {'kind': 'audio', 'count': 0, 'results': []}

        rows = []
        for path in sorted(search_root.rglob('*.mp3')):
            relative = path.relative_to(audio_dir)
            haystack = str(relative).lower()
            if query and query not in haystack:
                continue
            raw_url = f'/static/audio/{relative.as_posix()}'
            rows.append({
                'name': path.name,
                'track': path.stem.replace('_', '.'),
                'unit': relative.parts[0] if len(relative.parts) > 1 else '',
                'url': raw_url,
                'preview_url': protected_media_url(raw_url),
            })
            if len(rows) >= 250:
                break
        return {'kind': 'audio', 'count': len(rows), 'results': rows}


# ── Exercise content normalizers ──────────────────────────────────────────────
# Each normalizer handles both content formats (sentences/items) used in the project.

def _choose_correct_sentences(content):
    """
    Returns list of dicts with keys: options (list), correct (int index).
    Handles format: {sentences: [{before, options, after, correct}]}
                 or {items: [{sentence, options, correct_index}]}
    """
    if content.get('sentences'):
        return content['sentences']
    if content.get('items'):
        return [
            {'options': item.get('options', []), 'correct': item.get('correct_index', item.get('correct', 0))}
            for item in content['items']
        ]
    return []


def _fill_blank_sentences(content):
    """
    Returns list of dicts with keys: answer (str), alternatives (list, optional).
    Handles format: {sentences: [{text, answer}]}
                 or {items: [{sentence, answer}]}
    """
    if content.get('sentences'):
        return content['sentences']
    if content.get('items'):
        return content['items']
    return []


def _listening_questions(content):
    """
    Returns list of dicts with keys: question (str), options (list), correct (int index).
    Handles format: {questions: [{question, options, correct}]}
                 or {items: [{question/sentence, options, correct_index/correct}]}
    """
    if content.get('questions'):
        return content['questions']
    if content.get('items'):
        return [
            {
                'question': item.get('question', item.get('sentence', '')),
                'options': item.get('options', []),
                'correct': item.get('correct_index', item.get('correct', 0)),
            }
            for item in content['items']
        ]
    return []


def _scorable_rows(rows, content=None):
    """The first row is the guided example when an exercise has real work after it."""
    configured = (content or {}).get('example_count')
    start = configured if isinstance(configured, int) else (1 if len(rows) >= 2 else 0)
    return rows[max(0, min(start, len(rows))):]


def _normalize_written_answer(value):
    """Compare learner writing without penalizing case, spacing, or final punctuation."""
    value = str(value or '').replace('’', "'").replace('‘', "'").strip().lower()
    value = re.sub(r'\s+', ' ', value)
    return value.rstrip(' .!?')


def _grade_written_rows(rows, user_answers):
    if not rows:
        return False, 0
    correct_count = 0
    for index, row in enumerate(rows):
        accepted = [row.get('answer', ''), *(row.get('alternatives') or [])]
        accepted = {_normalize_written_answer(answer) for answer in accepted if answer}
        given = _normalize_written_answer(user_answers[index] if index < len(user_answers) else '')
        if given and given in accepted:
            correct_count += 1
    score = round((correct_count / len(rows)) * 100)
    return score == 100, score


# ── Exercise grading ──────────────────────────────────────────────────────────

def _grade_exercise(exercise, user_answer):
    """
    Returns (is_correct: bool, score: int 0-100).

    Submission formats by exercise type:
      choose_correct → { answers: [selectedOptionIdx, ...] }  (index per sentence)
      fill_blank     → { answers: ["typed text", ...] }        (index per sentence)
      matching       → { matches: {"0": rightOrigIdx, "1": rightOrigIdx, ...} }
                       key = left item index (str), value = right item original index
      listening      → { answers: {"0": selectedOptionIdx, ...} }
                       key = question index (str), value = selected option index
      speaking       → any (always 100)
      word_order     → { answers: ["complete sentence", ...] }
      written_answer → { answers: ["complete answer", ...] }
    """
    content = exercise.content
    etype = exercise.type

    if etype == 'choose_correct':
        sentences = _scorable_rows(_choose_correct_sentences(content), content)
        user_answers = user_answer.get('answers', [])
        if not sentences:
            return False, 0
        correct_count = sum(
            1 for i, s in enumerate(sentences)
            if i < len(user_answers) and user_answers[i] == s.get('correct', s.get('correct_index'))
        )
        score = round((correct_count / len(sentences)) * 100)
        return score == 100, score

    if etype == 'fill_blank' or (etype in ('reading', 'listening') and content.get('sentences')):
        sentences = _scorable_rows(_fill_blank_sentences(content), content)
        user_answers = user_answer.get('answers', [])
        if not sentences:
            return False, 0
        correct_count = 0
        for i, s in enumerate(sentences):
            expected_raw = s.get('answer', '')
            given_raw = user_answers[i] if i < len(user_answers) else ''
            if isinstance(expected_raw, list):
                expected = [_normalize_written_answer(value) for value in expected_raw]
                given_values = given_raw if isinstance(given_raw, list) else [given_raw]
                given = [_normalize_written_answer(value) for value in given_values]
                matches = bool(given) and given == expected
            else:
                expected = _normalize_written_answer(expected_raw)
                alternatives = [_normalize_written_answer(a) for a in s.get('alternatives', [])]
                given = _normalize_written_answer(given_raw)
                matches = bool(given) and given in ([expected] + alternatives)
            if matches:
                correct_count += 1
        score = round((correct_count / len(sentences)) * 100)
        return score == 100, score

    if etype == 'matching' or (etype == 'listening' and content.get('left')):
        # Format 1: {left:[...], right:[...], pairs:[0,1,...]}  pairs[i] = correct right index for left[i]
        # Format 2: {pairs:[{left:"...", right:"..."},...]}
        if 'left' in content and 'right' in content:
            left = content['left']
            right = content['right']
            correct_pairs = content.get('pairs', list(range(len(left))))  # pairs[i] = right orig idx
            configured_start = content.get('example_count')
            start = configured_start if isinstance(configured_start, int) else (1 if len(left) >= 2 else 0)
            start = max(0, min(start, len(left)))
            total = len(left) - start
            user_matches = user_answer.get('matches', {})  # {"leftIdx": rightOrigIdx}
            correct_count = sum(
                1 for i in range(start, len(left))
                if str(i) in user_matches and int(user_matches[str(i)]) == correct_pairs[i]
            )
        else:
            obj_pairs = content.get('pairs', [])  # [{left:"...", right:"..."}]
            obj_pairs = _scorable_rows(obj_pairs, content)
            total = len(obj_pairs)
            correct_map = {p['left']: p['right'] for p in obj_pairs}
            user_matches_list = user_answer.get('matches', [])  # [{left:"...", right:"..."}]
            correct_count = sum(
                1 for m in user_matches_list
                if correct_map.get(m.get('left')) == m.get('right')
            )
        if not total:
            return False, 0
        score = round((correct_count / total) * 100)
        return score == 100, score

    if etype in ('listening', 'reading'):
        questions = _scorable_rows(_listening_questions(content), content)
        user_answers = user_answer.get('answers', {})  # {"qIdx": selectedOptionIdx} or list
        if not questions:
            return False, 0
        correct_count = sum(
            1 for i, q in enumerate(questions)
            if (
                (isinstance(user_answers, list) and i < len(user_answers) and user_answers[i] == q.get('correct', q.get('correct_index', 0)))
                or (
                    isinstance(user_answers, dict)
                    and str(i) in user_answers
                    and user_answers[str(i)] == q.get('correct', q.get('correct_index', 0))
                )
            )
        )
        score = round((correct_count / len(questions)) * 100)
        return score == 100, score

    if etype == 'speaking':
        return True, 100

    if etype == 'word_order':
        rows = _scorable_rows(content.get('items', []), content)
        return _grade_written_rows(rows, user_answer.get('answers', []))

    if etype == 'written_answer':
        rows = _scorable_rows(content.get('questions', []), content)
        return _grade_written_rows(rows, user_answer.get('answers', []))

    return False, 0


def _build_feedback(exercise, user_answer, is_correct):
    """Returns the correct answers so the student can see what was right."""
    content = exercise.content
    etype = exercise.type

    if etype == 'choose_correct':
        sentences = _choose_correct_sentences(content)
        return {
            'correct_indices': [s.get('correct', s.get('correct_index', 0)) for s in sentences],
        }

    if etype == 'fill_blank' or (etype in ('reading', 'listening') and content.get('sentences')):
        sentences = _fill_blank_sentences(content)
        return {
            'correct_answers': [s.get('answer') for s in sentences],
        }

    if etype == 'matching' or (etype == 'listening' and content.get('left')):
        if 'left' in content and 'right' in content:
            left = content['left']
            right = content['right']
            pairs = content.get('pairs', list(range(len(left))))
            return {
                'correct_pairs': [{'left': left[i], 'right': right[pairs[i]]} for i in range(len(left))],
            }
        return {'correct_pairs': content.get('pairs', [])}

    if etype in ('listening', 'reading'):
        questions = _scorable_rows(_listening_questions(content), content)
        return {
            'correct_indices': [q.get('correct', q.get('correct_index', 0)) for q in questions],
        }

    if etype == 'word_order':
        return {
            'correct_answers': [row.get('answer') for row in content.get('items', [])],
        }

    if etype == 'written_answer':
        return {
            'correct_answers': [row.get('answer') for row in content.get('questions', [])],
        }

    return {}


# ── Exercise submit ───────────────────────────────────────────────────────────

class ExerciseSubmitView(APIView):
    """
    Student submits answer for one exercise. Saves ExerciseAttempt, returns score + feedback.

    Body: { exercise_id: N, answer: <format by type> }

    fill_blank       → { answers: ["are", "am", ...] }   (index-aligned to content.items)
    choose_correct   → { selected_index: N }
    listening        → { selected_index: N }
    matching         → { matches: [{ left: "...", right: "..." }, ...] }
    speaking         → { text: "..." }                   (always 100 points)
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        exercise_id = request.data.get('exercise_id')
        user_answer = request.data.get('answer', {})

        if not exercise_id:
            return Response({'detail': 'exercise_id required'}, status=400)

        try:
            exercise = Exercise.objects.select_related('lesson').get(pk=exercise_id)
        except Exercise.DoesNotExist:
            return Response({'detail': 'Exercise not found'}, status=404)

        if not is_platform_admin(request.user):
            from courses.views import (
                _is_lesson_locked, _lesson_locked_reason, _student_lessons_queryset,
            )
            ordered = list(_student_lessons_queryset(request.user))
            if _is_lesson_locked(request.user, exercise.lesson, ordered):
                return Response(
                    {'detail': _lesson_locked_reason(request.user, exercise.lesson, ordered)},
                    status=403,
                )

        is_correct, score = _grade_exercise(exercise, user_answer)

        feedback = _build_feedback(exercise, user_answer, is_correct)
        attempt = ExerciseAttempt.objects.create(
            user=request.user,
            exercise=exercise,
            lesson=exercise.lesson,
            exercise_type=exercise.type,
            instruction_snapshot=exercise.localized_instruction(
                getattr(request.user, 'language', 'kaa')
            ),
            content_snapshot=exercise.content,
            user_answer=user_answer,
            feedback=feedback,
            score=score,
            is_correct=is_correct,
        )

        return Response({
            'attempt_id': attempt.id,
            'score': score,
            'is_correct': is_correct,
            'feedback': feedback,
        })


# ── Attempt history ───────────────────────────────────────────────────────────

class QuizAttemptListView(APIView):
    """
    Student → own quiz attempts          GET /api/quiz/attempts/?lesson_id=X
    Admin   → any student's attempts     GET /api/quiz/attempts/?student_id=X&lesson_id=Y
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        lesson_id = request.query_params.get('lesson_id')

        if is_platform_admin(request.user):
            student_id = request.query_params.get('student_id')
            qs = QuizAttempt.objects.select_related('user', 'lesson').prefetch_related('answers__quiz')
            if student_id:
                qs = qs.filter(user_id=student_id)
            if lesson_id:
                qs = qs.filter(lesson_id=lesson_id)
        else:
            qs = (
                QuizAttempt.objects
                .filter(user=request.user)
                .select_related('lesson')
                .prefetch_related('answers__quiz')
            )
            if lesson_id:
                qs = qs.filter(lesson_id=lesson_id)

        return Response(QuizAttemptSerializer(qs, many=True).data)


class ExerciseAttemptListView(APIView):
    """
    Student → own exercise attempts      GET /api/quiz/exercise-attempts/?lesson_id=X
    Admin   → any student's attempts     GET /api/quiz/exercise-attempts/?student_id=X&lesson_id=Y
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        lesson_id = request.query_params.get('lesson_id')

        if is_platform_admin(request.user):
            student_id = request.query_params.get('student_id')
            qs = ExerciseAttempt.objects.select_related('user', 'lesson', 'exercise')
            if student_id:
                qs = qs.filter(user_id=student_id)
            if lesson_id:
                qs = qs.filter(lesson_id=lesson_id)
        else:
            qs = (
                ExerciseAttempt.objects
                .filter(user=request.user)
                .select_related('lesson', 'exercise')
            )
            if lesson_id:
                qs = qs.filter(lesson_id=lesson_id)

        return Response(ExerciseAttemptSerializer(qs, many=True).data)


# ── Admin notifications ──────────────────────────────────────────────────────

class AdminNotificationListView(APIView):
    permission_classes = [IsPlatformAdmin]

    def get(self, request):
        base_qs = AdminNotification.objects.select_related('student', 'lesson', 'quiz_attempt')
        unread_count = base_qs.filter(is_read=False).count()
        qs = base_qs

        read_filter = request.query_params.get('status')
        student_id = request.query_params.get('student_id')
        if read_filter == 'unread':
            qs = qs.filter(is_read=False)
        elif read_filter == 'read':
            qs = qs.filter(is_read=True)
        if student_id:
            qs = qs.filter(student_id=student_id)

        rows = qs[:250]
        return Response({
            'count': qs.count(),
            'unread_count': unread_count,
            'results': AdminNotificationSerializer(rows, many=True).data,
        })


class AdminNotificationDetailView(APIView):
    permission_classes = [IsPlatformAdmin]

    def patch(self, request, pk):
        try:
            notification = AdminNotification.objects.select_related(
                'student', 'lesson', 'quiz_attempt'
            ).get(pk=pk)
        except AdminNotification.DoesNotExist:
            return Response({'detail': 'Not found'}, status=404)

        is_read = request.data.get('is_read')
        if not isinstance(is_read, bool):
            return Response({'detail': 'is_read must be boolean'}, status=400)
        notification.is_read = is_read
        notification.read_at = timezone.now() if is_read else None
        notification.save(update_fields=['is_read', 'read_at'])
        return Response(AdminNotificationSerializer(notification).data)


class AdminNotificationReadAllView(APIView):
    permission_classes = [IsPlatformAdmin]

    def post(self, request):
        updated = AdminNotification.objects.filter(is_read=False).update(
            is_read=True,
            read_at=timezone.now(),
        )
        return Response({'updated': updated, 'unread_count': 0})
