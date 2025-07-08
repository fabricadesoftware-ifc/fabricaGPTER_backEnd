from django.contrib import admin
from django.urls import path, include
from rest_framework import routers

from core.views.medico import MedicoViewSet
from core.views.paciente import PacienteViewSet
from core.views.exame import ExameViewSet

router = routers.DefaultRouter()
router.register(r'medicos', MedicoViewSet)
router.register(r'pacientes', PacienteViewSet)
router.register(r'exames', ExameViewSet)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include(router.urls)),
    path('api/pacientes/<int:paciente_id>/exames/', ExameViewSet.as_view({'get': 'exames_por_paciente', 'post': 'exames_por_paciente'})),
]