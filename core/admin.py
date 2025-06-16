from django.contrib import admin

from core.models import Paciente
from core.models import Medico
from core.models import Admin

# Register your models here.


admin.site.register(Paciente)
admin.site.register(Medico)
admin.site.register(Admin)