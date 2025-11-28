from django.contrib import admin
from django.urls import path, include
from rest_framework import routers

from core.views.admin import AdministradorViewSet
from core.views.paciente import PacienteViewSet
from core.views.profissional import ProfissionalViewSet
from core.views.teste import TesteViewSet

from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

router = routers.DefaultRouter()
router.register(r'administradores', AdministradorViewSet)
router.register(r'pacientes', PacienteViewSet)
router.register(r'profissionais', ProfissionalViewSet)
router.register(r'testes', TesteViewSet)


urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include(router.urls)),
    path('/', include(router.urls)),
    path('auth/', include('core.urls_auth')),
] + router.urls
