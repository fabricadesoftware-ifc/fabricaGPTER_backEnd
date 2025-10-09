from django.contrib import admin
from django.urls import path, include
from rest_framework import routers

from core.views.admin import AdministradorViewSet
from core.views.paciente import PacienteViewSet
from core.views.profissional import ProfissionalViewSet

from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

router = routers.DefaultRouter()
router.register(r'administradores', AdministradorViewSet)
router.register(r'pacientes', PacienteViewSet)
router.register(r'profissionais', ProfissionalViewSet)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include(router.urls)),
    path('/', include(router.urls)),
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
] + router.urls
