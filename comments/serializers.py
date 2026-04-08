from rest_framework import serializers
from .models import Comment


class CommentSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source='user.full_name', read_only=True)
    user_username = serializers.CharField(source='user.username', read_only=True)

    class Meta:
        model = Comment
        fields = ['id', 'user', 'user_name', 'user_username', 'lesson', 'message', 'created_at']
        read_only_fields = ['id', 'user', 'user_name', 'user_username', 'created_at']
