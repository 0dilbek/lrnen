from rest_framework import serializers
from .models import Quiz, Exercise, QuizAttempt, QuizAttemptAnswer, ExerciseAttempt


class QuizSerializer(serializers.ModelSerializer):
    class Meta:
        model = Quiz
        fields = ['id', 'lesson', 'question', 'options', 'correct_option_index']

    def validate_options(self, value):
        if not isinstance(value, list) or len(value) < 2:
            raise serializers.ValidationError('options must be a list with at least 2 items')
        return value


class QuizStudentSerializer(serializers.ModelSerializer):
    """Hides correct_option_index for students."""
    class Meta:
        model = Quiz
        fields = ['id', 'lesson', 'question', 'options']


class ExerciseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Exercise
        fields = ['id', 'lesson', 'type', 'instruction', 'content', 'has_audio', 'audio_url', 'order']

    def validate_content(self, value):
        if not isinstance(value, dict):
            raise serializers.ValidationError('content must be a JSON object')
        return value


# ── Attempt serializers ───────────────────────────────────────────────────────

class QuizAttemptAnswerSerializer(serializers.ModelSerializer):
    selected_text = serializers.SerializerMethodField()
    correct_text = serializers.SerializerMethodField()

    class Meta:
        model = QuizAttemptAnswer
        fields = [
            'id', 'quiz', 'question_snapshot', 'options_snapshot',
            'selected_index', 'selected_text',
            'correct_index', 'correct_text',
            'is_correct',
        ]

    def get_selected_text(self, obj):
        opts = obj.options_snapshot
        if isinstance(opts, list) and 0 <= obj.selected_index < len(opts):
            return opts[obj.selected_index]
        return None

    def get_correct_text(self, obj):
        opts = obj.options_snapshot
        if isinstance(opts, list) and 0 <= obj.correct_index < len(opts):
            return opts[obj.correct_index]
        return None


class QuizAttemptSerializer(serializers.ModelSerializer):
    answers = QuizAttemptAnswerSerializer(many=True, read_only=True)
    student_name = serializers.CharField(source='user.full_name', read_only=True)
    student_username = serializers.CharField(source='user.username', read_only=True)
    lesson_title = serializers.CharField(source='lesson.title', read_only=True)

    class Meta:
        model = QuizAttempt
        fields = [
            'id', 'student_name', 'student_username',
            'lesson', 'lesson_title',
            'score', 'correct_count', 'total_count',
            'submitted_at', 'answers',
        ]


class ExerciseAttemptSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source='user.full_name', read_only=True)
    student_username = serializers.CharField(source='user.username', read_only=True)
    lesson_title = serializers.CharField(source='lesson.title', read_only=True)
    exercise_type_display = serializers.SerializerMethodField()

    class Meta:
        model = ExerciseAttempt
        fields = [
            'id', 'student_name', 'student_username',
            'exercise', 'lesson', 'lesson_title',
            'exercise_type', 'exercise_type_display',
            'instruction_snapshot', 'user_answer',
            'score', 'is_correct',
            'submitted_at',
        ]

    def get_exercise_type_display(self, obj):
        labels = {
            'choose_correct': "To'g'ri so'zni tanlash",
            'fill_blank': "Bo'sh joy to'ldirish",
            'matching': 'Moslashtirish',
            'listening': 'Listening',
            'speaking': 'Speaking',
        }
        return labels.get(obj.exercise_type, obj.exercise_type)
