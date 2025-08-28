from rest_framework import viewsets

from rest_framework.permissions import IsAuthenticated

from core.models.clinica import Clinica
from core.serializers.clinica import ClinicaSerializer

class ClinicaViewSet(viewsets.ModelViewSet):
    queryset = Clinica.objects.all()
    serializer_class = ClinicaSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user

        if hasattr(user, "administrador"):
            return Clinica.objects.all()

        if hasattr(user, "funcionario"):
            return Clinica.objects.filter(id=user.funcionario.clinica.id)

        if hasattr(user, "paciente"):
            return Clinica.objects.filter(id=user.paciente.clinica.id)

        return Clinica.objects.none()