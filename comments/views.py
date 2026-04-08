from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions
from .models import Comment
from .serializers import CommentSerializer


class CommentListView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        lesson_id = request.query_params.get('lesson')
        qs = Comment.objects.select_related('user')
        if lesson_id:
            qs = qs.filter(lesson_id=lesson_id)
        return Response(CommentSerializer(qs, many=True).data)

    def post(self, request):
        serializer = CommentSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(user=request.user)
        return Response(serializer.data, status=201)


class CommentDetailView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self, pk):
        try:
            return Comment.objects.get(pk=pk)
        except Comment.DoesNotExist:
            return None

    def delete(self, request, pk):
        obj = self.get_object(pk)
        if not obj:
            return Response({'detail': 'Not found'}, status=404)
        if request.user.role != 'admin' and obj.user != request.user:
            return Response({'detail': 'Forbidden'}, status=403)
        obj.delete()
        return Response(status=204)
