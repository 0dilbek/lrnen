from rest_framework import serializers
from .models import Quiz, Exercise


class QuizSerializer(serializers.ModelSerializer):
    class Meta:
        model = Quiz
        fields = ['id', 'lesson', 'question', 'options', 'correct_option_index']

    def validate_options(self, value):
        if not isinstance(value, list) or len(value) < 2:
            raise serializers.ValidationError('options must be a list with at least 2 items')
        return value


class QuizStudentSerializer(serializers.ModelSerializer):
    """Hides correct_option_index for students"""
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
