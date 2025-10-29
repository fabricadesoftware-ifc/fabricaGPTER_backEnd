from django.contrib import admin

from core.models.paciente import Paciente
from core.models.admin import Administrador
from core.models.profissional import Profissional
from core.models.teste import Teste

admin.site.register(Paciente)
admin.site.register(Administrador)
admin.site.register(Profissional)
admin.site.register(Teste)