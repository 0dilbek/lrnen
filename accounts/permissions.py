from rest_framework.permissions import BasePermission


def is_platform_admin(user):
    """Custom role and Django's staff flags both grant platform admin access."""
    return bool(
        getattr(user, 'is_authenticated', False)
        and (
            getattr(user, 'role', None) == 'admin'
            or getattr(user, 'is_staff', False)
            or getattr(user, 'is_superuser', False)
        )
    )


class IsPlatformAdmin(BasePermission):
    message = "Bu amal faqat administrator uchun ruxsat etilgan."

    def has_permission(self, request, view):
        return is_platform_admin(request.user)
