from django.contrib import admin
from django.urls import path, include
from rest_framework import routers

from core.views.estado import EstadoViewSet
from core.views.cidade import CidadeViewSet
from core.views.clinica import ClinicaViewSet

router = routers.DefaultRouter()
router.register(r'estados', EstadoViewSet)
router.register(r'cidades', CidadeViewSet)
router.register(r'clinicas', ClinicaViewSet)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include(router.urls)),
]

