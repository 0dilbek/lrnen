from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from .models import User
from .serializers import (
    LoginSerializer, UserSerializer, UserDetailSerializer,
    CreateStudentSerializer, UpdateStudentSerializer,
)


def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)
    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }


class LoginView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        username = serializer.validated_data['username']
        password = serializer.validated_data['password']

        user = authenticate(request, username=username, password=password)
        if user is None:
            return Response(
                {'detail': 'Login yoki parol noto\'g\'ri.'},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        tokens = get_tokens_for_user(user)
        return Response({
            'tokens': tokens,
            'user': UserSerializer(user).data,
        }, status=status.HTTP_200_OK)


class MeView(APIView):
    def get(self, request):
        return Response(UserSerializer(request.user).data)

    def put(self, request):
        serializer = UserSerializer(request.user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


class StudentListView(APIView):
    def get(self, request):
        if request.user.role != 'admin':
            return Response({'detail': 'Forbidden'}, status=403)
        students = User.objects.filter(role='student').order_by('-created_at')
        return Response(UserDetailSerializer(students, many=True).data)

    def post(self, request):
        if request.user.role != 'admin':
            return Response({'detail': 'Forbidden'}, status=403)
        serializer = CreateStudentSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        student = serializer.save()
        return Response(UserDetailSerializer(student).data, status=status.HTTP_201_CREATED)


class StudentDetailView(APIView):
    def _get_student(self, pk):
        try:
            return User.objects.get(pk=pk, role='student')
        except User.DoesNotExist:
            return None

    def get(self, request, pk):
        if request.user.role != 'admin':
            return Response({'detail': 'Forbidden'}, status=403)
        student = self._get_student(pk)
        if not student:
            return Response({'detail': 'Not found'}, status=404)
        from courses.models import UserProgress
        from courses.serializers import UserProgressSerializer
        progress = UserProgress.objects.filter(user=student).select_related('lesson')
        return Response({
            'user': UserDetailSerializer(student).data,
            'progress': UserProgressSerializer(progress, many=True).data,
        })

    def patch(self, request, pk):
        if request.user.role != 'admin':
            return Response({'detail': 'Forbidden'}, status=403)
        student = self._get_student(pk)
        if not student:
            return Response({'detail': 'Not found'}, status=404)
        serializer = UpdateStudentSerializer(student, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(UserDetailSerializer(student).data)

    def delete(self, request, pk):
        if request.user.role != 'admin':
            return Response({'detail': 'Forbidden'}, status=403)
        student = self._get_student(pk)
        if not student:
            return Response({'detail': 'Not found'}, status=404)
        student.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class LeaderboardView(APIView):
    def get(self, request):
        from courses.models import UserProgress
        from django.db.models import Avg, Count, Q

        students = User.objects.filter(role='student', is_active=True)
        result = []
        for student in students:
            progress = UserProgress.objects.filter(user=student)
            completed = progress.filter(status='completed').count()
            avg_score = progress.aggregate(avg=Avg('score'))['avg'] or 0
            xp = sum(
                100 + (p.score or 0) if p.status == 'completed' else round((p.score or 0) * 0.3)
                for p in progress
            )
            result.append({
                'id': student.id,
                'full_name': student.full_name,
                'username': student.username,
                'completed': completed,
                'avg_score': round(avg_score),
                'xp': xp,
            })

        result.sort(key=lambda x: x['xp'], reverse=True)
        # Rank qo'shish
        for i, r in enumerate(result):
            r['rank'] = i + 1
        # Faqat top 20
        return Response(result[:20])
