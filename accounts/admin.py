from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ['username', 'full_name', 'role', 'language', 'is_active', 'created_at']
    list_filter = ['role', 'language', 'is_active']
    search_fields = ['username', 'full_name']
    ordering = ['-created_at']
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Info', {'fields': ('full_name', 'role', 'language')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser')}),
    )
    add_fieldsets = (
        (None, {'fields': ('username', 'full_name', 'role', 'language', 'password1', 'password2')}),
    )
    filter_horizontal = []
