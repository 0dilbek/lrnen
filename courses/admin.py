from django.contrib import admin
from .models import Category, Lesson, UserProgress


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'description', 'created_at']
    search_fields = ['name']


@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    list_display = ['title', 'category', 'order', 'created_at']
    list_filter = ['category']
    search_fields = ['title']
    ordering = ['order']


@admin.register(UserProgress)
class UserProgressAdmin(admin.ModelAdmin):
    list_display = ['user', 'lesson', 'status', 'score', 'updated_at']
    list_filter = ['status']
    search_fields = ['user__phone', 'lesson__title']
