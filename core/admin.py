from django.contrib import admin

from core.models.paciente import Paciente
from core.models.admin import Administrador
from core.models.profissional import Profissional

admin.site.register(Paciente)
admin.site.register(Administrador)
admin.site.register(Profissional)