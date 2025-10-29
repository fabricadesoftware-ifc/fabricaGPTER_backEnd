from rest_framework import viewsets
from core.models.teste import Teste
from core.serializers.teste import TesteSerializer

class TesteViewSet(viewsets.ModelViewSet):
    queryset = Teste.objects.all()
    serializer_class = TesteSerializer
    
