from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework import routers

from core.views.admin import AdministradorViewSet
from core.views.paciente import PacienteViewSet
from core.views.profissional import ProfissionalViewSet
from core.views.teste import TesteViewSet
from core.views.user import UsuarioViewSet

from core.views.auth import RegisterView, MeView, RegisterPacienteView, RegisterProfissionalView, RegisterAdministradorView
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from uploader.router import router as uploader_router

router = routers.DefaultRouter()
router.register(r'administradores', AdministradorViewSet)
router.register(r'pacientes', PacienteViewSet)
router.register(r'profissionais', ProfissionalViewSet)
router.register(r'testes', TesteViewSet)
router.register(r'usuarios', UsuarioViewSet)



urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include(router.urls)),
    path('api/', include(router.urls)),
    path("api/media/", include(uploader_router.urls)),
    path('auth/register/', RegisterView.as_view(), name='register'),
    path('auth/register/paciente/', RegisterPacienteView.as_view(), name='register_paciente'),
    path('auth/register/profissional/', RegisterProfissionalView.as_view(), name='register_profissional'),
    path('auth/register/administrador/', RegisterAdministradorView.as_view(), name='register_administrador'),
    path('auth/login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('auth/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('auth/me/', MeView.as_view(), name='me'),
]

urlpatterns += static(settings.MEDIA_ENDPOINT, document_root=settings.MEDIA_ROOT)