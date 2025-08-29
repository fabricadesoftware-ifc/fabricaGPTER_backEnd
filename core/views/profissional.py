from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from core.models.profissional import Profissional
from core.serializers.profissional import ProfissionalSerializer
from core.permissions.permissions import IsAdminOrProfissional  

class ProfissionalViewSet(viewsets.ModelViewSet):
    queryset = Profissional.objects.all()
    serializer_class = ProfissionalSerializer
    permission_classes = [IsAuthenticated, IsAdminOrProfissional]

    def get_queryset(self):
        user = self.request.user

        if hasattr(user, "administrador"):
            return Profissional.objects.all()

        if hasattr(user, "profissional"):
            return Profissional.objects.filter(id=user.profissional.id)

        return Profissional.objects.none()
