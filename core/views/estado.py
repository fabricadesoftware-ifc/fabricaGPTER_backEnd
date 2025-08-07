from rest_framework import viewsets

from core.models.estado import Estado
from core.serializers.estado import EstadoSerializer

class EstadoViewSet(viewsets.ModelViewSet):
    queryset = Estado.objects.all()
    serializer_class = EstadoSerializer