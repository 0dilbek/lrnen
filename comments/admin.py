from django.contrib import admin
from .models import Comment


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ['user', 'lesson', 'message', 'created_at']
    list_filter = ['lesson']
    search_fields = ['user__phone', 'message']
