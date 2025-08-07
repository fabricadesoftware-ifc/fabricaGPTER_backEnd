from rest_framework import viewsets

from core.models.cidade import Cidade
from core.serializers.cidade import CidadeSerializer

class CidadeViewSet(viewsets.ModelViewSet):
    queryset = Cidade.objects.all()
    serializer_class = CidadeSerializer