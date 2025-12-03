from rest_framework import viewsets
from core.models.user import UsuarioBase
from core.serializers.user import UserSerializer

class UsuarioViewSet(viewsets.ModelViewSet):
    queryset = UsuarioBase.objects.all()
    serializer_class = UserSerializer
    


