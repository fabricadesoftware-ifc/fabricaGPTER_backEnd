from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin

from .models import AccessProfile, ProfessionalProfile
from patients.models import Patient

User = get_user_model()


@admin.register(ProfessionalProfile)
class ProfessionalProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'phone', 'birth_date', 'cpf')
    search_fields = ('user__username', 'user__email', 'user__first_name', 'user__last_name', 'cpf')
    autocomplete_fields = ('user',)


class ProfessionalProfileInline(admin.StackedInline):
    model = ProfessionalProfile
    extra = 1
    max_num = 1
    fields = ('phone', 'birth_date', 'cpf', 'photo')
    verbose_name = 'Informações do profissional'
    verbose_name_plural = 'Informações do profissional'


class PatientProfileInline(admin.StackedInline):
    model = Patient
    fk_name = 'user'
    extra = 0
    max_num = 1
    fields = ('phone', 'birth_date', 'cpf', 'photo')
    verbose_name = 'Informações do paciente'
    verbose_name_plural = 'Informações do paciente'


admin.site.unregister(User)


@admin.register(User)
class UserAdmin(DjangoUserAdmin):
    inlines = (ProfessionalProfileInline,)

    def get_inline_instances(self, request, obj=None):
        if obj is None or not hasattr(obj, 'access_profile'):
            return []
        if obj.access_profile.role == AccessProfile.Role.PROFESSIONAL:
            inline_classes = (ProfessionalProfileInline,)
        elif obj.access_profile.role == AccessProfile.Role.PATIENT:
            inline_classes = (PatientProfileInline,)
        else:
            return []
        return [inline(self.model, self.admin_site) for inline in inline_classes]


@admin.register(AccessProfile)
class AccessProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'role')
    list_filter = ('role',)
    search_fields = ('user__username',)
    autocomplete_fields = ('user',)
