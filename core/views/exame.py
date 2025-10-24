from rest_framework import viewsets
from core.models.exame import Exame
from core.serializers.exame import ExameSerializer

class ExameViewSet(viewsets.ModelViewSet):
    queryset = Exame.objects.all()
    serializer_class = ExameSerializer
    