from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from rest_framework.parsers import FormParser, MultiPartParser
from django.db.models import Min, Q
from django.conf import settings
from django.core import signing
from django.http import FileResponse, HttpResponse
from django.utils.http import content_disposition_header
import mimetypes
from pathlib import Path
from .models import Category, Lesson, UserProgress, Vocabulary, Level, MediaAsset
from .serializers import CategorySerializer, LessonSerializer, UserProgressSerializer, VocabularySerializer, LevelSerializer
from englishLMS.media_security import protected_media_url, resolve_protected_token
from accounts.permissions import IsPlatformAdmin, is_platform_admin


MEDIA_RULES = {
    'image': {
        'extensions': {'.jpg', '.jpeg', '.png', '.webp', '.gif'},
        'content_prefix': 'image/',
        'max_size': lambda: settings.MAX_IMAGE_UPLOAD_SIZE,
    },
    'audio': {
        'extensions': {'.mp3', '.m4a', '.aac', '.wav', '.ogg', '.webm'},
        'content_prefix': 'audio/',
        'max_size': lambda: settings.MAX_AUDIO_UPLOAD_SIZE,
    },
    'video': {
        'extensions': {'.mp4', '.webm', '.mov', '.m4v'},
        'content_prefix': 'video/',
        'max_size': lambda: settings.MAX_VIDEO_UPLOAD_SIZE,
    },
}

GENERIC_UPLOAD_CONTENT_TYPES = {
    '',
    'application/octet-stream',
    'binary/octet-stream',
}


def _asset_row(asset):
    raw_url = asset.file.url
    return {
        'id': asset.id,
        'kind': asset.kind,
        'name': asset.original_name,
        'content_type': asset.content_type,
        'size': asset.size,
        'url': raw_url,
        'preview_url': protected_media_url(raw_url),
        'created_at': asset.created_at,
    }


class MediaAssetListView(APIView):
    permission_classes = [IsPlatformAdmin]
    parser_classes = [MultiPartParser, FormParser]

    def get(self, request):
        assets = MediaAsset.objects.all()
        kind = request.query_params.get('kind')
        if kind in MEDIA_RULES:
            assets = assets.filter(kind=kind)
        return Response([_asset_row(asset) for asset in assets[:500]])

    def post(self, request):
        kind = request.data.get('kind')
        upload = request.FILES.get('file')
        if kind not in MEDIA_RULES or not upload:
            return Response({'detail': 'kind va file majburiy'}, status=400)

        rule = MEDIA_RULES[kind]
        extension = Path(upload.name).suffix.lower()
        content_type = (upload.content_type or '').lower()
        if extension not in rule['extensions']:
            return Response({'detail': f'{extension or "Fayl"} formati ruxsat etilmagan'}, status=400)
        if (
            content_type not in GENERIC_UPLOAD_CONTENT_TYPES
            and not content_type.startswith(rule['content_prefix'])
        ):
            return Response({'detail': 'Fayl turi tanlangan media turiga mos emas'}, status=400)
        if upload.size > rule['max_size']():
            limit_mb = rule['max_size']() // (1024 * 1024)
            return Response({'detail': f'Fayl {limit_mb} MB dan katta bo‘lmasligi kerak'}, status=400)

        asset = MediaAsset.objects.create(
            kind=kind,
            file=upload,
            original_name=Path(upload.name).name[:255],
            content_type=content_type or mimetypes.guess_type(upload.name)[0] or '',
            size=upload.size,
            uploaded_by=request.user,
        )
        return Response(_asset_row(asset), status=201)


class MediaAssetDetailView(APIView):
    permission_classes = [IsPlatformAdmin]

    def delete(self, request, pk):
        try:
            asset = MediaAsset.objects.get(pk=pk)
        except MediaAsset.DoesNotExist:
            return Response({'detail': 'Not found'}, status=404)
        asset.file.delete(save=False)
        asset.delete()
        return Response(status=204)


class ProtectedMediaAccessView(APIView):
    """Validate a short-lived signature, then delegate byte ranges to Nginx."""
    permission_classes = [permissions.AllowAny]
    authentication_classes = []

    def get(self, request, token):
        try:
            root, relative, target = resolve_protected_token(token)
        except (signing.BadSignature, signing.SignatureExpired):
            return Response({'detail': 'Media havolasi yaroqsiz yoki eskirgan'}, status=404)

        content_type = mimetypes.guess_type(target.name)[0] or 'application/octet-stream'
        if settings.USE_X_ACCEL_REDIRECT:
            response = HttpResponse(content_type=content_type)
            internal_root = '_protected_media' if root == 'media' else '_protected_static'
            response['X-Accel-Redirect'] = f'/{internal_root}/{relative}'
            response['Content-Disposition'] = content_disposition_header(False, target.name)
        else:
            response = FileResponse(
                target.open('rb'),
                content_type=content_type,
                as_attachment=False,
                filename=target.name,
            )
        response['Cache-Control'] = 'private, no-store, max-age=0'
        response['Pragma'] = 'no-cache'
        response['X-Content-Type-Options'] = 'nosniff'
        response['Cross-Origin-Resource-Policy'] = 'same-origin'
        response['Accept-Ranges'] = 'bytes'
        return response


class CategoryListView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        categories = Category.objects.all()
        return Response(CategorySerializer(categories, many=True).data)

    def post(self, request):
        if not is_platform_admin(request.user):
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
        if not is_platform_admin(request.user):
            return Response({'detail': 'Forbidden'}, status=403)
        obj = self.get_object(pk)
        if not obj:
            return Response({'detail': 'Not found'}, status=404)
        serializer = CategorySerializer(obj, data=request.data, partial=True)
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


class LevelListView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        levels = Level.objects.all()
        return Response(LevelSerializer(levels, many=True).data)


def _student_lessons_queryset(user, base_qs=None):
    """Student curriculum ordered by level first, then lesson order."""
    qs = base_qs if base_qs is not None else Lesson.objects.all()
    if is_platform_admin(user):
        return qs.order_by('order', 'id')

    level_ids = list(user.levels.values_list('id', flat=True))
    if not level_ids:
        default_level = Level.objects.order_by('order', 'id').first()
        if not default_level:
            return qs.order_by('order', 'id')
        level_ids = [default_level.id]

    return (
        qs.filter(levels__id__in=level_ids)
        .annotate(
            curriculum_level_order=Min(
                'levels__order',
                filter=Q(levels__id__in=level_ids),
            )
        )
        .distinct()
        .order_by('curriculum_level_order', 'order', 'id')
    )


def _get_visible_lesson_ids(user, lessons):
    """
    O'quvchi faqat quyidagilarni ko'radi:
      - yakunlangan darslar
      - hozirgi ochiq dars (ketma-ket birinchi tugallanmagan)
    Kelajakdagi darslar umuman ko'rinmaydi.
    """
    if is_platform_admin(user):
        return {lesson.id for lesson in lessons}

    # Caller passes the curriculum order (level → lesson). Re-sorting only by
    # lesson.order would interleave A1/A2/B1 units that share the same number.
    ordered = list(lessons)
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
    if is_platform_admin(user):
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


def _get_next_lesson(user, lesson):
    """Berilgan darsdan keyingi dars (order bo'yicha)."""
    ordered = list(_student_lessons_queryset(user))
    for i, l in enumerate(ordered):
        if l.id == lesson.id:
            if i + 1 < len(ordered):
                return ordered[i + 1]
            return None
    return None


class LessonListView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        qs = Lesson.objects.select_related('category').prefetch_related('levels').all()
        search = request.query_params.get('search', '')
        category = request.query_params.get('category', '')
        level = request.query_params.get('level', '')

        if not is_platform_admin(request.user):
            qs = _student_lessons_queryset(request.user, qs)

        if search:
            qs = qs.filter(Q(title__icontains=search) | Q(description__icontains=search))
        if category:
            qs = qs.filter(category_id=category)
        if level:
            qs = qs.filter(levels__slug=level)

        lessons = list(qs if not is_platform_admin(request.user) else qs.order_by('order', 'id'))

        # Ro'yxatda barcha biriktirilgan darslar ko'rinadi. Kelajakdagi darslar
        # yashirilmaydi — UI ularni yo'l xaritasida qulflangan holda chiqaradi.
        # Dars detail endpointidagi tekshiruv bevosita kirishni hamon bloklaydi.
        full_ordered = list(_student_lessons_queryset(request.user)) if not is_platform_admin(request.user) else lessons
        full_ids = [l.id for l in full_ordered]
        completed_ids = set()
        if not is_platform_admin(request.user) and full_ids:
            completed_ids = set(
                UserProgress.objects.filter(
                    user=request.user, lesson_id__in=full_ids, status='completed'
                ).values_list('lesson_id', flat=True)
            )

        data = LessonSerializer(lessons, many=True, context={'request': request}).data
        result = []
        for lesson, row in zip(lessons, data):
            row = dict(row)
            is_locked = _is_lesson_locked(
                request.user, lesson, full_ordered, completed_ids
            )
            row['is_locked'] = is_locked
            row['locked_reason'] = (
                "Oldingi dars testidan kamida 60% oling."
                if is_locked else None
            )
            if is_locked and not is_platform_admin(request.user):
                # Roadmap locked lessons' names are visible, their media is not.
                row['video_url'] = None
            result.append(row)
        return Response(result)

    def post(self, request):
        if not is_platform_admin(request.user):
            return Response({'detail': 'Forbidden'}, status=403)
        serializer = LessonSerializer(data=request.data, context={'request': request})
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

        if not is_platform_admin(request.user):
            all_lessons = list(_student_lessons_queryset(request.user))
            visible_ids = _get_visible_lesson_ids(request.user, all_lessons)
            if obj.id not in visible_ids:
                return Response({'detail': 'Not found'}, status=404)

        data = dict(LessonSerializer(obj, context={'request': request}).data)
        ordered = list(_student_lessons_queryset(request.user)) if not is_platform_admin(request.user) else [obj]
        data['is_locked'] = _is_lesson_locked(request.user, obj, ordered)
        data['locked_reason'] = (
            "Oldingi dars testidan kamida 60% oling."
            if data['is_locked'] else None
        )
        data['unlock_score'] = 60

        next_lesson = _get_next_lesson(request.user, obj) if not is_platform_admin(request.user) else None
        data['next_lesson_id'] = next_lesson.id if next_lesson else None
        data['next_lesson_title'] = next_lesson.localized_title(request.user.language) if next_lesson else None
        return Response(data)

    def put(self, request, pk):
        if not is_platform_admin(request.user):
            return Response({'detail': 'Forbidden'}, status=403)
        obj = self.get_object(pk)
        if not obj:
            return Response({'detail': 'Not found'}, status=404)
        serializer = LessonSerializer(
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


class VocabularyListView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        lesson_id = request.query_params.get('lesson')
        qs = Vocabulary.objects.all()
        if lesson_id:
            qs = qs.filter(lesson_id=lesson_id)
        return Response(
            VocabularySerializer(qs, many=True, context={'request': request}).data
        )

    def post(self, request):
        if not is_platform_admin(request.user):
            return Response({'detail': 'Forbidden'}, status=403)
        serializer = VocabularySerializer(data=request.data, context={'request': request})
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
        if not is_platform_admin(request.user):
            return Response({'detail': 'Forbidden'}, status=403)
        obj = self.get_object(pk)
        if not obj:
            return Response({'detail': 'Not found'}, status=404)
        serializer = VocabularySerializer(
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


class UserProgressView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        progress = UserProgress.objects.filter(user=request.user).select_related('lesson')
        return Response(
            UserProgressSerializer(progress, many=True, context={'request': request}).data
        )

    def post(self, request):
        lesson_id = request.data.get('lesson')
        if not lesson_id:
            return Response({'detail': 'lesson is required'}, status=400)
        try:
            lesson = Lesson.objects.get(pk=lesson_id)
        except Lesson.DoesNotExist:
            return Response({'detail': 'Lesson not found'}, status=404)

        if not is_platform_admin(request.user):
            ordered = list(_student_lessons_queryset(request.user))
            if _is_lesson_locked(request.user, lesson, ordered):
                return Response({
                    'detail': "Oldingi dars testidan kamida 60% olish kerak."
                }, status=403)
            if request.data.get('status') == 'completed':
                return Response({
                    'detail': "Dars faqat yakuniy testdan kamida 60% olinganda tugallanadi."
                }, status=400)

        progress, _ = UserProgress.objects.get_or_create(
            user=request.user,
            lesson=lesson,
        )
        # Yakunlangan darsni qayta "jarayonda" ga tushirmaslik
        payload = dict(request.data)
        if progress.status == 'completed' and payload.get('status') == 'in-progress':
            payload.pop('status', None)

        serializer = UserProgressSerializer(
            progress, data=payload, partial=True, context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


class StatsView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        if is_platform_admin(request.user):
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
