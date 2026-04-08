from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions
from .models import Quiz, Exercise
from .serializers import QuizSerializer, QuizStudentSerializer, ExerciseSerializer


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


class QuizSubmitView(APIView):
    """Student submits answers and gets score"""
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        answers = request.data.get('answers', [])  # [{quiz_id, selected_index}]
        if not answers:
            return Response({'detail': 'answers required'}, status=400)

        results = []
        correct_count = 0
        for ans in answers:
            quiz_id = ans.get('quiz_id')
            selected = ans.get('selected_index')
            try:
                quiz = Quiz.objects.get(pk=quiz_id)
                is_correct = quiz.correct_option_index == selected
                if is_correct:
                    correct_count += 1
                results.append({
                    'quiz_id': quiz_id,
                    'is_correct': is_correct,
                    'correct_option_index': quiz.correct_option_index,
                })
            except Quiz.DoesNotExist:
                results.append({'quiz_id': quiz_id, 'error': 'not found'})

        total = len(answers)
        score = round((correct_count / total) * 100) if total else 0

        # Update UserProgress score
        lesson_id = request.data.get('lesson_id')
        if lesson_id:
            from courses.models import UserProgress, Lesson
            try:
                lesson = Lesson.objects.get(pk=lesson_id)
                progress, _ = UserProgress.objects.get_or_create(user=request.user, lesson=lesson)
                progress.score = score
                if score >= 60:
                    progress.status = 'completed'
                else:
                    progress.status = 'in-progress'
                progress.save()
            except Lesson.DoesNotExist:
                pass

        return Response({
            'score': score,
            'correct': correct_count,
            'total': total,
            'results': results,
        })


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
