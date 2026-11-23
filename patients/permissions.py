from rest_framework.permissions import BasePermission

from accounts.models import AccessProfile


class IsProfessional(BasePermission):
    message = 'Acesso restrito a profissionais.'

    def has_permission(self, request, view):
        user = request.user
        if not (user and user.is_authenticated and user.is_active):
            return False
        try:
            return user.access_profile.role == AccessProfile.Role.PROFESSIONAL
        except AccessProfile.DoesNotExist:
            return False
