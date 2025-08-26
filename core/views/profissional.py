from rest_framework import viewsets
from core.models.profissional import Profissional
from core.serializers.profissional import ProfissionalSerializer

class ProfissionalViewSet(viewsets.ModelViewSet):
    queryset = Profissional.objects.all()
    serializer_class = ProfissionalSerializer