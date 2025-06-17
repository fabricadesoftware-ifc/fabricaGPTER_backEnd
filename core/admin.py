"""from django.contrib import admin

from core.models import Paciente
from core.models import Medico
from core.models import Admin

# Register your models here.


admin.site.register(Paciente)
admin.site.register(Medico)
admin.site.register(Admin)"""
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from core.models.user import CustomUser
from core.models.medico import Medico
from core.models.paciente import Paciente


class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display = ('username', 'email', 'role', 'is_staff', 'is_active')
    list_filter = ('role', 'is_staff', 'is_active')
    fieldsets = UserAdmin.fieldsets + (
        (None, {'fields': ('role',)}),
    )


admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(Medico)
admin.site.register(Paciente)
