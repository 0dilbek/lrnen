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
        ('speaking', 'Speaking'),
    ]
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE, related_name='exercises')
    type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    instruction = models.TextField()
    content = models.JSONField()
    has_audio = models.BooleanField(default=False)
    audio_url = models.CharField(max_length=500, blank=True, null=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order', 'id']

    def __str__(self):
        return f"{self.get_type_display()}: {self.instruction[:50]}"


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
    user_answer = models.JSONField()
    score = models.IntegerField(default=0)               # 0-100
    is_correct = models.BooleanField(default=False)      # True only if score == 100
    submitted_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-submitted_at']

    def __str__(self):
        return f"{self.user.username} – {self.exercise_type} – {self.score}% ({self.submitted_at:%Y-%m-%d %H:%M})"
