from django.contrib import admin
from .models import (
    AdminNotification,
    Exercise,
    ExerciseAttempt,
    Quiz,
    QuizAttempt,
    QuizAttemptAnswer,
)


@admin.register(Quiz)
class QuizAdmin(admin.ModelAdmin):
    list_display = ['question', 'lesson', 'correct_option_index']
    list_filter = ['lesson']
    search_fields = ['question']


@admin.register(Exercise)
class ExerciseAdmin(admin.ModelAdmin):
    list_display = ['instruction_kaa', 'instruction_uz', 'type', 'lesson', 'source', 'has_audio', 'order']
    list_filter = ['type', 'source', 'has_audio', 'lesson']
    search_fields = ['instruction', 'instruction_kaa', 'instruction_uz']
    list_editable = ['order', 'has_audio']


class QuizAttemptAnswerInline(admin.TabularInline):
    model = QuizAttemptAnswer
    extra = 0
    readonly_fields = ['quiz', 'question_snapshot', 'options_snapshot', 'selected_index', 'correct_index', 'is_correct']
    can_delete = False


@admin.register(QuizAttempt)
class QuizAttemptAdmin(admin.ModelAdmin):
    list_display = ['user', 'lesson', 'score', 'correct_count', 'total_count', 'submitted_at']
    list_filter = ['lesson', 'submitted_at']
    search_fields = ['user__username', 'user__full_name', 'lesson__title']
    readonly_fields = ['user', 'lesson', 'score', 'correct_count', 'total_count', 'submitted_at']
    inlines = [QuizAttemptAnswerInline]

    def has_add_permission(self, request):
        return False


@admin.register(ExerciseAttempt)
class ExerciseAttemptAdmin(admin.ModelAdmin):
    list_display = ['user', 'lesson', 'exercise_type', 'score', 'is_correct', 'submitted_at']
    list_filter = ['exercise_type', 'is_correct', 'lesson', 'submitted_at']
    search_fields = ['user__username', 'user__full_name', 'lesson__title']
    readonly_fields = [
        'user', 'exercise', 'lesson',
        'exercise_type', 'instruction_snapshot',
        'content_snapshot', 'user_answer', 'feedback',
        'score', 'is_correct', 'submitted_at',
    ]

    def has_add_permission(self, request):
        return False


@admin.register(AdminNotification)
class AdminNotificationAdmin(admin.ModelAdmin):
    list_display = ['student', 'lesson_title_snapshot', 'score', 'is_read', 'created_at']
    list_filter = ['is_read', 'event_type', 'created_at']
    search_fields = ['student__username', 'student__full_name', 'lesson_title_snapshot']
    readonly_fields = [
        'event_type', 'student', 'lesson', 'lesson_title_snapshot',
        'quiz_attempt', 'score', 'created_at',
    ]

    def has_add_permission(self, request):
        return False
