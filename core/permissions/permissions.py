# from rest_framework.permissions import BasePermission

# class IsAdmin(BasePermission):
#     def has_permission(self, request, view):
#         return request.user.is_authenticated and request.user.role == 'admin'


# class IsMedico(BasePermission):
#     def has_permission(self, request, view):
#         return request.user.is_authenticated and request.user.role == 'medico'


# class IsPaciente(BasePermission):
#     def has_permission(self, request, view):
#         return request.user.is_authenticated and request.user.role == 'paciente'
