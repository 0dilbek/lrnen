from rest_framework import serializers
from .models import Category, Lesson, UserProgress, Vocabulary


class CategorySerializer(serializers.ModelSerializer):
    lesson_count = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = ['id', 'name', 'description', 'lesson_count', 'created_at']

    def get_lesson_count(self, obj):
        return obj.lessons.count()


class LessonSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)

    class Meta:
        model = Lesson
        fields = ['id', 'title', 'description', 'video_url', 'category', 'category_name', 'difficulty', 'order', 'created_at']


class VocabularySerializer(serializers.ModelSerializer):
    class Meta:
        model = Vocabulary
        fields = ['id', 'lesson', 'word', 'translation', 'example', 'order']


class UserProgressSerializer(serializers.ModelSerializer):
    lesson_title = serializers.CharField(source='lesson.title', read_only=True)

    class Meta:
        model = UserProgress
        fields = ['id', 'lesson', 'lesson_title', 'status', 'score', 'updated_at']
        read_only_fields = ['id', 'updated_at']
