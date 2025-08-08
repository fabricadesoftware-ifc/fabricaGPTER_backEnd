from django.contrib import admin

from core.models.estado import Estado
from core.models.cidade import Cidade
from core.models.clinica import Clinica

admin.site.register(Estado)
admin.site.register(Cidade)
admin.site.register(Clinica)