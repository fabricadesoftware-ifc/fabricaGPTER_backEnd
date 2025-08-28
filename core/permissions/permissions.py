from rest_framework.permissions import BasePermission

class IsAdmin(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and hasattr(request.user, "administrador")


class IsFuncionario(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and hasattr(request.user, "funcionario")


class IsPaciente(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and hasattr(request.user, "paciente")
