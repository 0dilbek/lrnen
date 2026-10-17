from django.db import models
from django.conf import settings
from courses.models import Lesson


class Quiz(models.Model):
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE, related_name='quizzes')
    question = models.TextField()
    options = models.JSONField()  # list of strings
    correct_option_index = models.PositiveSmallIntegerField()

    def __str__(self):
        return f"Quiz: {self.question[:50]}"


class Exercise(models.Model):
    TYPE_CHOICES = [
        ('choose_correct', "To'g'ri so'zni tanlash"),
        ('fill_blank', "Bo'sh joy to'ldirish"),
        ('matching', 'Moslashtirish'),
        ('listening', 'Listening'),
        ('reading', 'Reading'),
        ('speaking', 'Speaking'),
        ('word_order', "So'zlarni tartiblash"),
        ('written_answer', 'Yozma javob'),
    ]
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE, related_name='exercises')
    type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    instruction = models.TextField()
    instruction_kaa = models.TextField(blank=True)
    instruction_uz = models.TextField(blank=True)
    content = models.JSONField()
    has_audio = models.BooleanField(default=False)
    audio_url = models.CharField(max_length=500, blank=True, null=True)
    order = models.PositiveIntegerField(default=0)
    source = models.CharField(max_length=100, blank=True, db_index=True)
    source_unit = models.PositiveSmallIntegerField(null=True, blank=True)

    class Meta:
        ordering = ['order', 'id']

    def __str__(self):
        return f"{self.get_type_display()}: {self.instruction[:50]}"

    def localized_instruction(self, language='kaa'):
        return getattr(self, f'instruction_{language}', '') or self.instruction


# ── Attempt tracking ──────────────────────────────────────────────────────────

class QuizAttempt(models.Model):
    """One full quiz submission for a lesson (contains multiple answers)."""
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='quiz_attempts')
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE, related_name='quiz_attempts')
    score = models.IntegerField(default=0)          # 0-100
    correct_count = models.IntegerField(default=0)
    total_count = models.IntegerField(default=0)
    submitted_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-submitted_at']

    def __str__(self):
        return f"{self.user.username} – {self.lesson.title} – {self.score}% ({self.submitted_at:%Y-%m-%d %H:%M})"


class QuizAttemptAnswer(models.Model):
    """One answer within a QuizAttempt (snapshot saved so quiz edits don't alter history)."""
    attempt = models.ForeignKey(QuizAttempt, on_delete=models.CASCADE, related_name='answers')
    quiz = models.ForeignKey(Quiz, on_delete=models.SET_NULL, null=True)
    question_snapshot = models.TextField()
    options_snapshot = models.JSONField()
    selected_index = models.IntegerField()
    correct_index = models.IntegerField()
    is_correct = models.BooleanField()

    def __str__(self):
        mark = '✓' if self.is_correct else '✗'
        return f"{mark} {self.question_snapshot[:40]}"


class ExerciseAttempt(models.Model):
    """One exercise submission. Stores what the student answered and the result."""
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='exercise_attempts')
    exercise = models.ForeignKey(Exercise, on_delete=models.SET_NULL, null=True, related_name='attempts')
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE, related_name='exercise_attempts')
    exercise_type = models.CharField(max_length=20)     # snapshot
    instruction_snapshot = models.TextField()            # snapshot
    content_snapshot = models.JSONField(default=dict, blank=True)
    user_answer = models.JSONField()
    feedback = models.JSONField(default=dict, blank=True)
    score = models.IntegerField(default=0)               # 0-100
    is_correct = models.BooleanField(default=False)      # True only if score == 100
    submitted_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-submitted_at']

    def __str__(self):
        return f"{self.user.username} – {self.exercise_type} – {self.score}% ({self.submitted_at:%Y-%m-%d %H:%M})"


class AdminNotification(models.Model):
    """Persistent admin inbox event created when a student completes a lesson."""

    EVENT_LESSON_COMPLETED = 'lesson_completed'
    EVENT_CHOICES = [
        (EVENT_LESSON_COMPLETED, 'Lesson completed'),
    ]

    event_type = models.CharField(max_length=32, choices=EVENT_CHOICES, default=EVENT_LESSON_COMPLETED)
    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='admin_notifications',
    )
    lesson = models.ForeignKey(
        Lesson,
        on_delete=models.SET_NULL,
        null=True,
        related_name='admin_notifications',
    )
    lesson_title_snapshot = models.CharField(max_length=200)
    quiz_attempt = models.OneToOneField(
        QuizAttempt,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='admin_notification',
    )
    score = models.PositiveSmallIntegerField(default=0)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    read_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']
        constraints = [
            models.UniqueConstraint(
                fields=['student', 'lesson', 'event_type'],
                name='unique_student_lesson_admin_event',
            ),
        ]
        indexes = [
            models.Index(fields=['is_read', '-created_at'], name='admin_notif_read_idx'),
            models.Index(fields=['student', '-created_at'], name='admin_notif_student_idx'),
        ]

    def __str__(self):
        state = 'read' if self.is_read else 'unread'
        return f"{self.student.username} – {self.lesson_title_snapshot} ({state})"
