from rest_framework import serializers
from .models import (
    AdminNotification,
    Exercise,
    ExerciseAttempt,
    Quiz,
    QuizAttempt,
    QuizAttemptAnswer,
)
from englishLMS.media_security import protect_content_urls, protected_media_url
from accounts.permissions import is_platform_admin


class QuizSerializer(serializers.ModelSerializer):
    class Meta:
        model = Quiz
        fields = ['id', 'lesson', 'question', 'options', 'correct_option_index']

    def validate_options(self, value):
        if not isinstance(value, list) or len(value) < 2:
            raise serializers.ValidationError('options must be a list with at least 2 items')
        if any(not isinstance(option, str) or not option.strip() for option in value):
            raise serializers.ValidationError('all options must be non-empty strings')
        return value

    def validate(self, attrs):
        attrs = super().validate(attrs)
        options = attrs.get('options', getattr(self.instance, 'options', []))
        correct_index = attrs.get(
            'correct_option_index',
            getattr(self.instance, 'correct_option_index', None),
        )
        if (
            not isinstance(correct_index, int)
            or isinstance(correct_index, bool)
            or not 0 <= correct_index < len(options)
        ):
            raise serializers.ValidationError({
                'correct_option_index': 'To‘g‘ri javob indeksi variantlar oralig‘ida bo‘lishi kerak.'
            })
        return attrs


class QuizStudentSerializer(serializers.ModelSerializer):
    """Hides correct_option_index for students."""
    class Meta:
        model = Quiz
        fields = ['id', 'lesson', 'question', 'options']


class ExerciseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Exercise
        fields = [
            'id', 'lesson', 'type', 'instruction', 'instruction_kaa', 'instruction_uz',
            'content', 'has_audio', 'audio_url', 'order', 'source', 'source_unit',
        ]

    def validate_content(self, value):
        if not isinstance(value, dict):
            raise serializers.ValidationError('content must be a JSON object')
        return value

    def to_representation(self, instance):
        data = super().to_representation(instance)
        request = self.context.get('request')
        language = getattr(getattr(request, 'user', None), 'language', 'kaa')
        language = language if language in {'kaa', 'uz'} else 'kaa'
        data['instruction'] = instance.localized_instruction(language)
        data['content_language'] = language
        if not request or not is_platform_admin(request.user):
            data.pop('instruction_kaa', None)
            data.pop('instruction_uz', None)
            data['audio_url'] = protected_media_url(data.get('audio_url'))
            data['content'] = protect_content_urls(data.get('content'))
        return data

    def validate(self, attrs):
        """Validate the structured editors without breaking legacy imported rows."""
        attrs = super().validate(attrs)
        exercise_type = attrs.get('type', getattr(self.instance, 'type', None))
        content = attrs.get('content', getattr(self.instance, 'content', {})) or {}

        def validate_choice_rows(rows, label):
            if not isinstance(rows, list) or not rows:
                raise serializers.ValidationError({'content': f'{label} uchun savollar kiritilishi kerak.'})
            for index, row in enumerate(rows, start=1):
                options = row.get('options') if isinstance(row, dict) else None
                correct = row.get('correct', row.get('correct_index')) if isinstance(row, dict) else None
                if not isinstance(options, list) or len(options) < 2:
                    raise serializers.ValidationError({'content': f'{index}-savolda kamida 2 ta variant bo‘lishi kerak.'})
                normalized = [str(option).strip().casefold() for option in options]
                if len(normalized) != len(set(normalized)):
                    raise serializers.ValidationError({'content': f'{index}-savolda takroriy variant bor.'})
                if not isinstance(correct, int) or not 0 <= correct < len(options):
                    raise serializers.ValidationError({'content': f'{index}-savolning to‘g‘ri javob indeksi noto‘g‘ri.'})

        if exercise_type == 'choose_correct':
            validate_choice_rows(
                content.get('sentences') or content.get('items') or content.get('questions'),
                'Variant tanlash',
            )

        if exercise_type == 'fill_blank':
            rows = content.get('sentences') or content.get('items') or []
            if not isinstance(rows, list) or not rows:
                raise serializers.ValidationError({'content': 'Bo‘sh joy mashqi uchun gaplar kiritilishi kerak.'})
            for index, row in enumerate(rows, start=1):
                text = str((row or {}).get('text') or (row or {}).get('sentence') or '')
                answer = (row or {}).get('answer')
                blank_count = text.count('___')
                answer_count = len(answer) if isinstance(answer, list) else int(answer is not None and str(answer).strip() != '')
                if blank_count == 0 or blank_count != answer_count:
                    raise serializers.ValidationError({
                        'content': f'{index}-qatorda bo‘sh joylar ({blank_count}) va javoblar ({answer_count}) soni teng emas.'
                    })

        if exercise_type == 'matching':
            left = content.get('left') or []
            right = content.get('right') or []
            pairs = content.get('pairs') or []
            if len(left) < 2 or len(left) != len(pairs):
                raise serializers.ValidationError({'content': 'Moslashtirish juftliklari to‘liq emas.'})
            if any(not isinstance(value, int) or not 0 <= value < len(right) for value in pairs):
                raise serializers.ValidationError({'content': 'Moslashtirish javob indekslaridan biri noto‘g‘ri.'})

        if exercise_type == 'reading':
            pages = content.get('pages', [])
            questions = content.get('questions') or content.get('sentences') or []
            if not isinstance(pages, list) or not pages:
                raise serializers.ValidationError({
                    'content': "Reading uchun kamida bitta kitob sahifasini tanlang."
                })
            if content.get('questions'):
                validate_choice_rows(content['questions'], 'Reading')

        if exercise_type == 'word_order':
            items = content.get('items', [])
            if not isinstance(items, list) or len(items) < 2:
                raise serializers.ValidationError({
                    'content': "So‘z tartiblash uchun 1 ta namuna va kamida 1 ta savol kiriting."
                })
            for item in items:
                if not isinstance(item, dict) or not item.get('answer') or len(item.get('tokens', [])) < 2:
                    raise serializers.ValidationError({
                        'content': "Har bir qatorda kamida 2 ta so‘z va to‘liq javob bo‘lishi kerak."
                    })

        if exercise_type == 'written_answer':
            questions = content.get('questions', [])
            if not isinstance(questions, list) or len(questions) < 2:
                raise serializers.ValidationError({
                    'content': "Yozma mashq uchun 1 ta namuna va kamida 1 ta savol kiriting."
                })
            for question in questions:
                if not isinstance(question, dict) or not question.get('prompt') or not question.get('answer'):
                    raise serializers.ValidationError({
                        'content': "Har bir savolda matn va to‘g‘ri javob bo‘lishi kerak."
                    })
            if not isinstance(questions, list) or len(questions) < 2:
                raise serializers.ValidationError({
                    'content': "Reading uchun 1 ta namuna va kamida 1 ta savol kiriting."
                })

        if exercise_type == 'listening':
            audio_url = attrs.get('audio_url', getattr(self.instance, 'audio_url', None))
            audio_urls = content.get('audio_urls') or []
            if not audio_url and not any(audio_urls):
                raise serializers.ValidationError({
                    'audio_url': "Listening uchun audio fayl yoki URL tanlang."
                })
            rows = (
                content.get('questions') or content.get('items') or
                content.get('sentences') or content.get('left') or []
            )
            if audio_urls:
                if not isinstance(audio_urls, list) or len(audio_urls) != len(rows):
                    raise serializers.ValidationError({
                        'content': 'Har bir listening qatori uchun audio qismi tartibi saqlanishi kerak.'
                    })
                if any(not isinstance(url, str) for url in audio_urls):
                    raise serializers.ValidationError({
                        'content': 'Audio qismlar URL ko‘rinishida bo‘lishi kerak.'
                    })
            if content.get('left'):
                left, right, pairs = content.get('left') or [], content.get('right') or [], content.get('pairs') or []
                if len(left) != len(pairs) or any(not isinstance(value, int) or not 0 <= value < len(right) for value in pairs):
                    raise serializers.ValidationError({'content': 'Listening moslashtirish juftliklari to‘liq emas.'})
            elif content.get('questions') or content.get('items'):
                validate_choice_rows(content.get('questions') or content.get('items'), 'Listening')

        return attrs


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
            'instruction_snapshot', 'content_snapshot',
            'user_answer', 'feedback',
            'score', 'is_correct',
            'submitted_at',
        ]

    def get_exercise_type_display(self, obj):
        labels = {
            'choose_correct': "To'g'ri so'zni tanlash",
            'fill_blank': "Bo'sh joy to'ldirish",
            'matching': 'Moslashtirish',
            'listening': 'Listening',
            'reading': 'Reading',
            'speaking': 'Speaking',
            'word_order': "So'zlarni tartiblash",
            'written_answer': 'Yozma javob',
        }
        return labels.get(obj.exercise_type, obj.exercise_type)


class AdminNotificationSerializer(serializers.ModelSerializer):
    student_name = serializers.SerializerMethodField()
    student_username = serializers.CharField(source='student.username', read_only=True)
    student_color = serializers.SerializerMethodField()
    lesson_title = serializers.SerializerMethodField()

    class Meta:
        model = AdminNotification
        fields = [
            'id', 'event_type',
            'student', 'student_name', 'student_username', 'student_color',
            'lesson', 'lesson_title', 'quiz_attempt', 'score',
            'is_read', 'created_at', 'read_at',
        ]
        read_only_fields = fields

    def get_student_name(self, obj):
        return obj.student.full_name or obj.student.username

    def get_student_color(self, obj):
        # Stable palette slot: the same student is always shown with the same color.
        return obj.student_id % 8

    def get_lesson_title(self, obj):
        return obj.lesson_title_snapshot or (obj.lesson.title if obj.lesson else '')
