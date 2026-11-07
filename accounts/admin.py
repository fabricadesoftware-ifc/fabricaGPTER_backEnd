from django.contrib import admin
from .models import AccessProfile


@admin.register(AccessProfile)
class AccessProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'role')
    list_filter = ('role',)
    search_fields = ('user__username',)
    autocomplete_fields = ('user',)
