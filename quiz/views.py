from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions
from .models import Quiz, Exercise, QuizAttempt, QuizAttemptAnswer, ExerciseAttempt
from .serializers import (
    QuizSerializer, QuizStudentSerializer, ExerciseSerializer,
    QuizAttemptSerializer, ExerciseAttemptSerializer,
)


# ── Quiz CRUD ─────────────────────────────────────────────────────────────────

class QuizListView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        lesson_id = request.query_params.get('lesson')
        qs = Quiz.objects.all()
        if lesson_id:
            qs = qs.filter(lesson_id=lesson_id)
        if request.user.role == 'admin':
            return Response(QuizSerializer(qs, many=True).data)
        return Response(QuizStudentSerializer(qs, many=True).data)

    def post(self, request):
        if request.user.role != 'admin':
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
        if request.user.role == 'admin':
            return Response(QuizSerializer(obj).data)
        return Response(QuizStudentSerializer(obj).data)

    def put(self, request, pk):
        if request.user.role != 'admin':
            return Response({'detail': 'Forbidden'}, status=403)
        obj = self.get_object(pk)
        if not obj:
            return Response({'detail': 'Not found'}, status=404)
        serializer = QuizSerializer(obj, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    def delete(self, request, pk):
        if request.user.role != 'admin':
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

    def post(self, request):
        answers = request.data.get('answers', [])
        lesson_id = request.data.get('lesson_id')

        if not answers:
            return Response({'detail': 'answers required'}, status=400)
        if not lesson_id:
            return Response({'detail': 'lesson_id required'}, status=400)

        from courses.models import UserProgress, Lesson
        try:
            lesson = Lesson.objects.get(pk=lesson_id)
        except Lesson.DoesNotExist:
            return Response({'detail': 'Lesson not found'}, status=404)

        results = []
        correct_count = 0
        answer_objs = []

        for ans in answers:
            quiz_id = ans.get('quiz_id')
            selected = ans.get('selected_index')
            try:
                quiz = Quiz.objects.get(pk=quiz_id)
            except Quiz.DoesNotExist:
                results.append({'quiz_id': quiz_id, 'error': 'not found'})
                continue

            is_correct = quiz.correct_option_index == selected
            if is_correct:
                correct_count += 1

            opts = quiz.options if isinstance(quiz.options, list) else []
            results.append({
                'quiz_id': quiz_id,
                'question': quiz.question,
                'options': opts,
                'selected_index': selected,
                'selected_text': opts[selected] if opts and selected is not None and 0 <= selected < len(opts) else None,
                'correct_index': quiz.correct_option_index,
                'correct_text': opts[quiz.correct_option_index] if opts and 0 <= quiz.correct_option_index < len(opts) else None,
                'is_correct': is_correct,
            })
            answer_objs.append({
                'quiz': quiz,
                'question_snapshot': quiz.question,
                'options_snapshot': quiz.options,
                'selected_index': selected if selected is not None else -1,
                'correct_index': quiz.correct_option_index,
                'is_correct': is_correct,
            })

        total = len(answer_objs)
        score = round((correct_count / total) * 100) if total else 0

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
        progress.score = score
        progress.status = 'completed' if score >= 60 else 'in-progress'
        progress.save()

        return Response({
            'attempt_id': attempt.id,
            'score': score,
            'correct': correct_count,
            'total': total,
            'results': results,
        })


# ── Exercise CRUD ─────────────────────────────────────────────────────────────

class ExerciseListView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        lesson_id = request.query_params.get('lesson')
        qs = Exercise.objects.all()
        if lesson_id:
            qs = qs.filter(lesson_id=lesson_id)
        return Response(ExerciseSerializer(qs, many=True).data)

    def post(self, request):
        if request.user.role != 'admin':
            return Response({'detail': 'Forbidden'}, status=403)
        serializer = ExerciseSerializer(data=request.data)
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
        if request.user.role != 'admin':
            return Response({'detail': 'Forbidden'}, status=403)
        obj = self.get_object(pk)
        if not obj:
            return Response({'detail': 'Not found'}, status=404)
        serializer = ExerciseSerializer(obj, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    def delete(self, request, pk):
        if request.user.role != 'admin':
            return Response({'detail': 'Forbidden'}, status=403)
        obj = self.get_object(pk)
        if not obj:
            return Response({'detail': 'Not found'}, status=404)
        obj.delete()
        return Response(status=204)


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
    """
    content = exercise.content
    etype = exercise.type

    if etype == 'choose_correct':
        sentences = _choose_correct_sentences(content)
        user_answers = user_answer.get('answers', [])
        if not sentences:
            return False, 0
        correct_count = sum(
            1 for i, s in enumerate(sentences)
            if i < len(user_answers) and user_answers[i] == s.get('correct', s.get('correct_index'))
        )
        score = round((correct_count / len(sentences)) * 100)
        return score == 100, score

    if etype == 'fill_blank':
        sentences = _fill_blank_sentences(content)
        user_answers = user_answer.get('answers', [])
        if not sentences:
            return False, 0
        correct_count = 0
        for i, s in enumerate(sentences):
            expected = s.get('answer', '').strip().lower()
            alternatives = [a.strip().lower() for a in s.get('alternatives', [])]
            given = str(user_answers[i]).strip().lower() if i < len(user_answers) else ''
            if given and given in ([expected] + alternatives):
                correct_count += 1
        score = round((correct_count / len(sentences)) * 100)
        return score == 100, score

    if etype == 'matching':
        # Format 1: {left:[...], right:[...], pairs:[0,1,...]}  pairs[i] = correct right index for left[i]
        # Format 2: {pairs:[{left:"...", right:"..."},...]}
        if 'left' in content and 'right' in content:
            left = content['left']
            right = content['right']
            correct_pairs = content.get('pairs', list(range(len(left))))  # pairs[i] = right orig idx
            total = len(left)
            user_matches = user_answer.get('matches', {})  # {"leftIdx": rightOrigIdx}
            correct_count = sum(
                1 for i in range(total)
                if str(i) in user_matches and int(user_matches[str(i)]) == correct_pairs[i]
            )
        else:
            obj_pairs = content.get('pairs', [])  # [{left:"...", right:"..."}]
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

    if etype == 'listening':
        questions = _listening_questions(content)
        user_answers = user_answer.get('answers', {})  # {"qIdx": selectedOptionIdx}
        if not questions:
            return False, 0
        correct_count = sum(
            1 for i, q in enumerate(questions)
            if str(i) in user_answers and user_answers[str(i)] == q.get('correct', q.get('correct_index', 0))
        )
        score = round((correct_count / len(questions)) * 100)
        return score == 100, score

    if etype == 'speaking':
        return True, 100

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

    if etype == 'fill_blank':
        sentences = _fill_blank_sentences(content)
        return {
            'correct_answers': [s.get('answer') for s in sentences],
        }

    if etype == 'matching':
        if 'left' in content and 'right' in content:
            left = content['left']
            right = content['right']
            pairs = content.get('pairs', list(range(len(left))))
            return {
                'correct_pairs': [{'left': left[i], 'right': right[pairs[i]]} for i in range(len(left))],
            }
        return {'correct_pairs': content.get('pairs', [])}

    if etype == 'listening':
        questions = _listening_questions(content)
        return {
            'correct_indices': [q.get('correct', q.get('correct_index', 0)) for q in questions],
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

        is_correct, score = _grade_exercise(exercise, user_answer)

        attempt = ExerciseAttempt.objects.create(
            user=request.user,
            exercise=exercise,
            lesson=exercise.lesson,
            exercise_type=exercise.type,
            instruction_snapshot=exercise.instruction,
            user_answer=user_answer,
            score=score,
            is_correct=is_correct,
        )

        return Response({
            'attempt_id': attempt.id,
            'score': score,
            'is_correct': is_correct,
            'feedback': _build_feedback(exercise, user_answer, is_correct),
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

        if request.user.role == 'admin':
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

        if request.user.role == 'admin':
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
