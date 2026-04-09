from django.db import models
from django.conf import settings


class Category(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = 'Categories'


class Level(models.Model):
    LEVEL_CHOICES = [
        ('a1', 'A1 Beginner'),
        ('a2', 'A2 Elementary'),
        ('b1', 'B1 Pre-Intermediate'),
        ('b2', 'B2 Intermediate'),
        ('c1', 'C1 Upper-Intermediate'),
        ('c2', 'C2 Advanced'),
        ('ielts', 'IELTS'),
    ]
    slug = models.CharField(max_length=10, choices=LEVEL_CHOICES, unique=True)
    order = models.PositiveIntegerField(default=0)

    def __str__(self):
        return dict(self.LEVEL_CHOICES).get(self.slug, self.slug)

    class Meta:
        ordering = ['order']


class Lesson(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    video_url = models.URLField()
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, related_name='lessons')
    levels = models.ManyToManyField(Level, blank=True, related_name='lessons')
    order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

    class Meta:
        ordering = ['order', 'created_at']


class Vocabulary(models.Model):
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE, related_name='vocabulary')
    word = models.CharField(max_length=100)           # English
    translation = models.CharField(max_length=200)    # Uzbek
    example = models.TextField(blank=True)            # Example sentence (optional)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order', 'id']

    def __str__(self):
        return f"{self.word} — {self.translation}"


class UserProgress(models.Model):
    STATUS_CHOICES = [('in-progress', 'In Progress'), ('completed', 'Completed')]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='progress')
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE, related_name='progress')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='in-progress')
    score = models.IntegerField(default=0)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('user', 'lesson')

    def __str__(self):
        return f"{self.user.username} - {self.lesson.title} ({self.status})"
