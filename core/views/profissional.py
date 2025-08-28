from rest_framework import viewsets

from rest_framework.permissions import IsAuthenticated

from core.permissions.permissions import IsFuncionario, IsAdmin


from core.models.profissional import Profissional
from core.serializers.profissional import ProfissionalSerializer

class ProfissionalViewSet(viewsets.ModelViewSet):
    queryset = Profissional.objects.all()
    serializer_class = ProfissionalSerializer
    permission_classes = [IsAuthenticated, IsFuncionario, IsAdmin]