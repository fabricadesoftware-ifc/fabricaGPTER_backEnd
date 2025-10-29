from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework import routers

from core.views.admin import AdministradorViewSet
from core.views.paciente import PacienteViewSet
from core.views.profissional import ProfissionalViewSet
from core.views.teste import TesteViewSet

from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from uploader.router import router as uploader_router

router = routers.DefaultRouter()
router.register(r'administradores', AdministradorViewSet)
router.register(r'pacientes', PacienteViewSet)
router.register(r'profissionais', ProfissionalViewSet)
router.register(r'testes', TesteViewSet)


urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include(router.urls)),
    path('/', include(router.urls)),
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path("api/media/", include(uploader_router.urls)),
] + router.urls

urlpatterns += static(settings.MEDIA_ENDPOINT, document_root=settings.MEDIA_ROOT)