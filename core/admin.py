from django.contrib import admin

from core.models import Paciente
from core.models import Medico

# Register your models here.


admin.site.register(Paciente)
admin.site.register(Medico)