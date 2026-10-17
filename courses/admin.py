from django.contrib import admin
from .models import Category, Lesson, UserProgress, Vocabulary, Level, MediaAsset


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'description', 'created_at']
    search_fields = ['name']


@admin.register(Level)
class LevelAdmin(admin.ModelAdmin):
    list_display = ['slug', '__str__', 'order', 'current_lesson']
    list_select_related = ['current_lesson']
    ordering = ['order']


@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    list_display = ['title_kaa', 'title_uz', 'category', 'order', 'created_at']
    list_filter = ['category', 'levels']
    search_fields = ['title', 'title_kaa', 'title_uz']
    filter_horizontal = ['levels']
    ordering = ['order']


@admin.register(Vocabulary)
class VocabularyAdmin(admin.ModelAdmin):
    list_display = ['word', 'translation_kaa', 'translation_uz', 'lesson', 'source_unit', 'order']
    list_filter = ['source', 'source_unit', 'lesson']
    search_fields = ['word', 'translation', 'translation_kaa', 'translation_uz']
    ordering = ['lesson', 'order', 'id']


@admin.register(UserProgress)
class UserProgressAdmin(admin.ModelAdmin):
    list_display = ['user', 'lesson', 'status', 'score', 'updated_at']
    list_filter = ['status']
    search_fields = ['user__phone', 'lesson__title']


@admin.register(MediaAsset)
class MediaAssetAdmin(admin.ModelAdmin):
    list_display = ['original_name', 'kind', 'size', 'uploaded_by', 'created_at']
    list_filter = ['kind', 'created_at']
    search_fields = ['original_name']
    readonly_fields = ['file', 'original_name', 'content_type', 'size', 'uploaded_by', 'created_at']
