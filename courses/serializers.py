from rest_framework import serializers
from .models import Category, Lesson, UserProgress, Vocabulary, Level
from englishLMS.media_security import protected_media_url
from accounts.permissions import is_platform_admin


class CategorySerializer(serializers.ModelSerializer):
    lesson_count = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = ['id', 'name', 'description', 'lesson_count', 'created_at']

    def get_lesson_count(self, obj):
        return obj.lessons.count()


class LevelSerializer(serializers.ModelSerializer):
    name = serializers.SerializerMethodField()
    current_lesson_id = serializers.IntegerField(read_only=True)

    class Meta:
        model = Level
        fields = ['id', 'slug', 'name', 'order', 'current_lesson_id']

    def get_name(self, obj):
        return str(obj)


class LessonSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)
    levels = LevelSerializer(many=True, read_only=True)
    level_ids = serializers.PrimaryKeyRelatedField(
        many=True, queryset=Level.objects.all(), source='levels', write_only=True, required=False
    )

    class Meta:
        model = Lesson
        fields = [
            'id', 'title', 'description', 'video_url',
            'title_kaa', 'title_uz', 'description_kaa', 'description_uz',
            'video_url_kaa', 'video_url_uz',
            'category', 'category_name', 'levels', 'level_ids', 'order', 'created_at',
        ]

    @staticmethod
    def _language(request):
        language = getattr(getattr(request, 'user', None), 'language', 'kaa')
        return language if language in {'kaa', 'uz'} else 'kaa'

    def to_representation(self, instance):
        data = super().to_representation(instance)
        request = self.context.get('request')
        language = self._language(request)
        data['title'] = instance.localized_title(language)
        data['description'] = instance.localized_description(language)
        data['video_url'] = instance.localized_video_url(language)
        data['content_language'] = language
        if not request or not is_platform_admin(request.user):
            data['video_url'] = protected_media_url(data.get('video_url'))
            for field in (
                'title_kaa', 'title_uz', 'description_kaa', 'description_uz',
                'video_url_kaa', 'video_url_uz',
            ):
                data.pop(field, None)
        return data


class VocabularySerializer(serializers.ModelSerializer):
    class Meta:
        model = Vocabulary
        fields = [
            'id', 'lesson', 'word', 'translation',
            'translation_kaa', 'translation_uz', 'example', 'order',
        ]

    def to_representation(self, instance):
        data = super().to_representation(instance)
        request = self.context.get('request')
        language = getattr(getattr(request, 'user', None), 'language', 'kaa')
        language = language if language in {'kaa', 'uz'} else 'kaa'
        data['translation'] = instance.localized_translation(language)
        data['content_language'] = language
        if not request or not is_platform_admin(request.user):
            data.pop('translation_kaa', None)
            data.pop('translation_uz', None)
        return data


class UserProgressSerializer(serializers.ModelSerializer):
    lesson_title = serializers.SerializerMethodField()

    class Meta:
        model = UserProgress
        fields = ['id', 'lesson', 'lesson_title', 'status', 'score', 'updated_at']
        read_only_fields = ['id', 'updated_at']

    def get_lesson_title(self, obj):
        request = self.context.get('request')
        language = getattr(getattr(request, 'user', None), 'language', 'kaa')
        return obj.lesson.localized_title(language if language in {'kaa', 'uz'} else 'kaa')
