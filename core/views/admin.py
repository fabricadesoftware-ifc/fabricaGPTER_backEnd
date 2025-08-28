from rest_framework import viewsets

from rest_framework.permissions import IsAuthenticated

from core.permissions.permissions import IsAdmin

from core.models.admin import Administrador
from core.serializers.admin import AdministradorSerializer

class AdministradorViewSet(viewsets.ModelViewSet):
    queryset = Administrador.objects.all()
    serializer_class = AdministradorSerializer
    permission_classes = [IsAuthenticated, IsAdmin]



