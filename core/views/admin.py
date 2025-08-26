from rest_framework import viewsets
from core.models.admin import Administrador
from core.serializers.admin import AdministradorSerializer

class AdministradorViewSet(viewsets.ModelViewSet):
    queryset = Administrador.objects.all()
    serializer_class = AdministradorSerializer

