from rest_framework.permissions import BasePermission

class IsAdmin(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and hasattr(request.user, "administrador")


class IsProfissional(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and hasattr(request.user, "profissional")


class IsPaciente(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and hasattr(request.user, "paciente")
    

class IsAdminOrProfissional(BasePermission):
    def has_permission(self, request, view):
        user = request.user
        if not user or not user.is_authenticated:
            return False
        return hasattr(user, "administrador") or hasattr(user, "profissional")


class IsAdminOrProfissionalOrSelf(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        user = request.user

        if hasattr(user, "administrador"):
            return True

        if hasattr(user, "profissional") and obj.profissional == user.profissional:
            return True

        if hasattr(user, "paciente") and obj.usuario == user:
            return True

        return False