from django.contrib import admin
from .models import Quiz, Exercise, QuizAttempt, QuizAttemptAnswer, ExerciseAttempt


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
        'user_answer', 'score', 'is_correct', 'submitted_at',
    ]

    def has_add_permission(self, request):
        return False
