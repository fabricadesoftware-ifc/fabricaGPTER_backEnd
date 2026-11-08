from django.contrib import admin
from django.urls import include, path
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

@api_view(['GET'])
@authentication_classes([])
@permission_classes([AllowAny])
def health_check(request):
    return Response({'status': 'ok'})

handler404 = 'accounts.errors.not_found'
handler500 = 'accounts.errors.server_error'

urlpatterns = [
    path('', health_check, name='root-health-check'),
    path('api/auth/', include('accounts.urls')),
    path('api/', include('patients.urls')),
    path('admin/', admin.site.urls),
    path('api/health/', health_check, name='health-check'),
]
