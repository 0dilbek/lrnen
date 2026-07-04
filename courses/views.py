from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from django.db.models import Q
from .models import Category, Lesson, UserProgress, Vocabulary, Level
from .serializers import CategorySerializer, LessonSerializer, UserProgressSerializer, VocabularySerializer, LevelSerializer


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


class LevelListView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        levels = Level.objects.all()
        return Response(LevelSerializer(levels, many=True).data)


def _student_lessons_queryset(user, base_qs=None):
    """O'quvchiga tegishli darslar (level bo'yicha)."""
    qs = base_qs if base_qs is not None else Lesson.objects.all()
    if user.role == 'student' and user.levels.exists():
        slugs = list(user.levels.values_list('slug', flat=True))
        qs = qs.filter(levels__slug__in=slugs).distinct()
    return qs.order_by('order', 'id')


def _get_visible_lesson_ids(user, lessons):
    """
    O'quvchi faqat quyidagilarni ko'radi:
      - yakunlangan darslar
      - hozirgi ochiq dars (ketma-ket birinchi tugallanmagan)
    Kelajakdagi darslar umuman ko'rinmaydi.
    """
    if user.role != 'student':
        return {lesson.id for lesson in lessons}

    ordered = sorted(lessons, key=lambda l: (l.order, l.id))
    if not ordered:
        return set()

    lesson_ids = [l.id for l in ordered]
    progress = UserProgress.objects.filter(user=user, lesson_id__in=lesson_ids)
    completed_ids = set(progress.filter(status='completed').values_list('lesson_id', flat=True))

    visible = set()
    for i, lesson in enumerate(ordered):
        if i == 0:
            visible.add(lesson.id)
            if lesson.id not in completed_ids:
                break
            continue
        prev = ordered[i - 1]
        if prev.id in completed_ids:
            visible.add(lesson.id)
            if lesson.id not in completed_ids:
                break
        else:
            break

    return visible


def _is_lesson_locked(user, lesson, ordered_lessons=None, completed_ids=None):
    """Oldingi dars yakunlanmagan bo'lsa bloklangan."""
    if user.role != 'student':
        return False

    if ordered_lessons is None:
        ordered_lessons = list(_student_lessons_queryset(user))
    if completed_ids is None:
        lesson_ids = [l.id for l in ordered_lessons]
        completed_ids = set(
            UserProgress.objects.filter(
                user=user, lesson_id__in=lesson_ids, status='completed'
            ).values_list('lesson_id', flat=True)
        )

    for i, l in enumerate(ordered_lessons):
        if l.id == lesson.id:
            if i == 0:
                return False
            return ordered_lessons[i - 1].id not in completed_ids
    return True


class LessonListView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        qs = Lesson.objects.select_related('category').prefetch_related('levels').all()
        search = request.query_params.get('search', '')
        category = request.query_params.get('category', '')
        level = request.query_params.get('level', '')

        # Student o'ziga biriktirilgan levellar bo'yicha avtomatik filter
        if request.user.role == 'student' and request.user.levels.exists():
            user_level_slugs = list(request.user.levels.values_list('slug', flat=True))
            qs = qs.filter(levels__slug__in=user_level_slugs).distinct()

        if search:
            qs = qs.filter(Q(title__icontains=search) | Q(description__icontains=search))
        if category:
            qs = qs.filter(category_id=category)
        if level:
            qs = qs.filter(levels__slug=level)

        lessons = list(qs.order_by('order', 'id'))

        if request.user.role == 'student':
            visible_ids = _get_visible_lesson_ids(request.user, lessons)
            lessons = [l for l in lessons if l.id in visible_ids]

        lesson_ids = [l.id for l in lessons]
        completed_ids = set()
        if request.user.role == 'student' and lesson_ids:
            completed_ids = set(
                UserProgress.objects.filter(
                    user=request.user, lesson_id__in=lesson_ids, status='completed'
                ).values_list('lesson_id', flat=True)
            )
        ordered = lessons

        data = LessonSerializer(lessons, many=True).data
        result = []
        for lesson, row in zip(lessons, data):
            row = dict(row)
            row['is_locked'] = _is_lesson_locked(
                request.user, lesson, ordered, completed_ids
            )
            result.append(row)
        return Response(result)

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

        if request.user.role == 'student':
            all_lessons = list(_student_lessons_queryset(request.user))
            visible_ids = _get_visible_lesson_ids(request.user, all_lessons)
            if obj.id not in visible_ids:
                return Response({'detail': 'Not found'}, status=404)

        data = dict(LessonSerializer(obj).data)
        ordered = list(_student_lessons_queryset(request.user)) if request.user.role == 'student' else [obj]
        data['is_locked'] = _is_lesson_locked(request.user, obj, ordered)
        return Response(data)

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
