from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from django.db.models import Q
from .models import Category, Lesson, UserProgress, Vocabulary
from .serializers import CategorySerializer, LessonSerializer, UserProgressSerializer, VocabularySerializer


class IsAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'admin'


class CategoryListView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        categories = Category.objects.all()
        return Response(CategorySerializer(categories, many=True).data)

    def post(self, request):
        if request.user.role != 'admin':
            return Response({'detail': 'Forbidden'}, status=403)
        serializer = CategorySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=201)


class CategoryDetailView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self, pk):
        try:
            return Category.objects.get(pk=pk)
        except Category.DoesNotExist:
            return None

    def get(self, request, pk):
        obj = self.get_object(pk)
        if not obj:
            return Response({'detail': 'Not found'}, status=404)
        return Response(CategorySerializer(obj).data)

    def put(self, request, pk):
        if request.user.role != 'admin':
            return Response({'detail': 'Forbidden'}, status=403)
        obj = self.get_object(pk)
        if not obj:
            return Response({'detail': 'Not found'}, status=404)
        serializer = CategorySerializer(obj, data=request.data, partial=True)
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


class LessonListView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        qs = Lesson.objects.select_related('category').all()
        search = request.query_params.get('search', '')
        category = request.query_params.get('category', '')
        if search:
            qs = qs.filter(Q(title__icontains=search) | Q(description__icontains=search))
        if category:
            qs = qs.filter(category_id=category)
        return Response(LessonSerializer(qs, many=True).data)

    def post(self, request):
        if request.user.role != 'admin':
            return Response({'detail': 'Forbidden'}, status=403)
        serializer = LessonSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=201)


class LessonDetailView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self, pk):
        try:
            return Lesson.objects.select_related('category').get(pk=pk)
        except Lesson.DoesNotExist:
            return None

    def get(self, request, pk):
        obj = self.get_object(pk)
        if not obj:
            return Response({'detail': 'Not found'}, status=404)
        return Response(LessonSerializer(obj).data)

    def put(self, request, pk):
        if request.user.role != 'admin':
            return Response({'detail': 'Forbidden'}, status=403)
        obj = self.get_object(pk)
        if not obj:
            return Response({'detail': 'Not found'}, status=404)
        serializer = LessonSerializer(obj, data=request.data, partial=True)
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


class VocabularyListView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        lesson_id = request.query_params.get('lesson')
        qs = Vocabulary.objects.all()
        if lesson_id:
            qs = qs.filter(lesson_id=lesson_id)
        return Response(VocabularySerializer(qs, many=True).data)

    def post(self, request):
        if request.user.role != 'admin':
            return Response({'detail': 'Forbidden'}, status=403)
        serializer = VocabularySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=201)


class VocabularyDetailView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self, pk):
        try:
            return Vocabulary.objects.get(pk=pk)
        except Vocabulary.DoesNotExist:
            return None

    def put(self, request, pk):
        if request.user.role != 'admin':
            return Response({'detail': 'Forbidden'}, status=403)
        obj = self.get_object(pk)
        if not obj:
            return Response({'detail': 'Not found'}, status=404)
        serializer = VocabularySerializer(obj, data=request.data, partial=True)
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


class UserProgressView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        progress = UserProgress.objects.filter(user=request.user).select_related('lesson')
        return Response(UserProgressSerializer(progress, many=True).data)

    def post(self, request):
        lesson_id = request.data.get('lesson')
        if not lesson_id:
            return Response({'detail': 'lesson is required'}, status=400)
        try:
            lesson = Lesson.objects.get(pk=lesson_id)
        except Lesson.DoesNotExist:
            return Response({'detail': 'Lesson not found'}, status=404)

        progress, _ = UserProgress.objects.get_or_create(
            user=request.user,
            lesson=lesson,
        )
        serializer = UserProgressSerializer(progress, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


class StatsView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        if request.user.role == 'admin':
            from accounts.models import User
            total_students = User.objects.filter(role='student').count()
            total_lessons = Lesson.objects.count()
            total_categories = Category.objects.count()
            total_progress = UserProgress.objects.count()
            completed = UserProgress.objects.filter(status='completed').count()
            return Response({
                'total_students': total_students,
                'total_lessons': total_lessons,
                'total_categories': total_categories,
                'total_progress': total_progress,
                'completed': completed,
            })
        else:
            progress = UserProgress.objects.filter(user=request.user)
            total = progress.count()
            completed = progress.filter(status='completed').count()
            avg_score = 0
            if total:
                scores = [p.score for p in progress if p.score]
                avg_score = sum(scores) / len(scores) if scores else 0
            return Response({
                'total_started': total,
                'completed': completed,
                'avg_score': round(avg_score, 1),
            })
