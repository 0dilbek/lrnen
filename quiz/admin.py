from django.contrib import admin
from .models import Quiz, Exercise


@admin.register(Quiz)
class QuizAdmin(admin.ModelAdmin):
    list_display = ['question', 'lesson', 'correct_option_index']
    list_filter = ['lesson']
    search_fields = ['question']


@admin.register(Exercise)
class ExerciseAdmin(admin.ModelAdmin):
    list_display = ['instruction', 'type', 'lesson', 'has_audio', 'order']
    list_filter = ['type', 'has_audio', 'lesson']
    search_fields = ['instruction']
    list_editable = ['order', 'has_audio']
    readonly_fields = ['type']
