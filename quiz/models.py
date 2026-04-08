from django.db import models
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
