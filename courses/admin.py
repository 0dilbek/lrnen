from django.contrib import admin
from .models import Category, Lesson, UserProgress, Level


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'description', 'created_at']
    search_fields = ['name']


@admin.register(Level)
class LevelAdmin(admin.ModelAdmin):
    list_display = ['slug', '__str__', 'order']
    ordering = ['order']


@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    list_display = ['title', 'category', 'order', 'created_at']
    list_filter = ['category', 'levels']
    search_fields = ['title']
    filter_horizontal = ['levels']
    ordering = ['order']


@admin.register(UserProgress)
class UserProgressAdmin(admin.ModelAdmin):
    list_display = ['user', 'lesson', 'status', 'score', 'updated_at']
    list_filter = ['status']
    search_fields = ['user__phone', 'lesson__title']
