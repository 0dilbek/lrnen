from django.db import models
from django.conf import settings
from pathlib import Path
import uuid


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
    current_lesson = models.ForeignKey(
        'Lesson',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='released_for_levels',
        help_text="O'quvchilar shu darsgacha kira oladi. Bo'sh bo'lsa birinchi dars ochiladi.",
    )

    def __str__(self):
        return dict(self.LEVEL_CHOICES).get(self.slug, self.slug)

    class Meta:
        ordering = ['order']


class Lesson(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    title_kaa = models.CharField(max_length=200, blank=True)
    title_uz = models.CharField(max_length=200, blank=True)
    description_kaa = models.TextField(blank=True)
    description_uz = models.TextField(blank=True)
    # YouTube URL yoki lokal /media/... yo'li.
    video_url = models.CharField(max_length=500, blank=True, null=True)
    video_url_kaa = models.CharField(max_length=500, blank=True, null=True)
    video_url_uz = models.CharField(max_length=500, blank=True, null=True)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, related_name='lessons')
    levels = models.ManyToManyField(Level, blank=True, related_name='lessons')
    order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

    def localized_title(self, language='kaa'):
        return getattr(self, f'title_{language}', '') or self.title

    def localized_description(self, language='kaa'):
        return getattr(self, f'description_{language}', '') or self.description

    def localized_video_url(self, language='kaa'):
        localized = getattr(self, f'video_url_{language}', None)
        if localized:
            return localized
        # Legacy rows belong to the Qoraqalpoq group only. Uzbek videos are
        # intentionally left empty until an administrator uploads them.
        return self.video_url if language == 'kaa' else None

    class Meta:
        ordering = ['order', 'created_at']


class Vocabulary(models.Model):
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE, related_name='vocabulary')
    word = models.CharField(max_length=100)           # English
    translation = models.CharField(max_length=200)    # Legacy Qoraqalpoq value
    translation_kaa = models.CharField(max_length=200, blank=True)
    translation_uz = models.CharField(max_length=200, blank=True)
    example = models.TextField(blank=True)            # Example sentence (optional)
    order = models.PositiveIntegerField(default=0)
    source = models.CharField(max_length=100, blank=True, db_index=True)
    source_unit = models.PositiveSmallIntegerField(null=True, blank=True)

    class Meta:
        ordering = ['order', 'id']

    def __str__(self):
        return f"{self.word} — {self.translation}"

    def localized_translation(self, language='kaa'):
        return getattr(self, f'translation_{language}', '') or self.translation


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


def protected_asset_path(instance, filename):
    extension = Path(filename).suffix.lower()[:12]
    return f'protected/{instance.kind}/{uuid.uuid4().hex}{extension}'


class MediaAsset(models.Model):
    KIND_CHOICES = [
        ('image', 'Image'),
        ('audio', 'Audio'),
        ('video', 'Video'),
    ]
    kind = models.CharField(max_length=10, choices=KIND_CHOICES)
    file = models.FileField(upload_to=protected_asset_path)
    original_name = models.CharField(max_length=255)
    content_type = models.CharField(max_length=120, blank=True)
    size = models.PositiveBigIntegerField(default=0)
    uploaded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='uploaded_media_assets',
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.kind}: {self.original_name}'
