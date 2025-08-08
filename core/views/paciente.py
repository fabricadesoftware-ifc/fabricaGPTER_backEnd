from rest_framework import viewsets

from core.models.paciente import Paciente

from core.serializers.paciente import PacienteSerializer

from core.permissions.medico import IsMedico
from core.permissions.admin import IsAdmin
from core.permissions.paciente import IsPaciente

from rest_framework.permissions import IsAuthenticated


class PacienteViewSet(viewsets.ModelViewSet):
    queryset = Paciente.objects.all()
    serializer_class = PacienteSerializer
    permission_classes = [IsAuthenticated, IsMedico | IsAdmin | IsPaciente]

    def get_queryset(self):
        user = self.request.user
        if user.role == 'admin':
            return Paciente.objects.all()
        elif user.role == 'medico':
            return Paciente.objects.filter(medico__user=user)
        elif user.role == 'paciente':
            return Paciente.objects.filter(user=user)
        return Paciente.objects.none()