from django.contrib import admin

from .models import Patient


@admin.register(Patient)
class PatientAdmin(admin.ModelAdmin):
    list_display = ('name', 'user', 'professional', 'status', 'created_at')
    list_filter = ('status', 'state')
    search_fields = ('name', 'user__username', 'cpf', 'email')
    autocomplete_fields = ('user', 'professional')
    readonly_fields = ('address', 'created_at', 'updated_at')
