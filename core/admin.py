from django.contrib import admin

from core.models.estado import Estado
from core.models.cidade import Cidade
from core.models.clinica import Clinica
from core.models.paciente import Paciente
from core.models.admin import Administrador
from core.models.profissional import Profissional

admin.site.register(Estado)
admin.site.register(Cidade)
admin.site.register(Clinica)
admin.site.register(Paciente)
admin.site.register(Administrador)
admin.site.register(Profissional)