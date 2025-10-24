from django.contrib import admin

from core.models.paciente import Paciente
from core.models.admin import Administrador
from core.models.profissional import Profissional
from core.models.exame import Exame

admin.site.register(Paciente)
admin.site.register(Administrador)
admin.site.register(Profissional)
admin.site.register(Exame)