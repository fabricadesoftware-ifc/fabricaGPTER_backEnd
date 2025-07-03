from rest_framework import viewsets

from core.models.medico import Medico
from core.models.paciente import Paciente

from core.serializers.medico import MedicoSerializer

from core.permissions.medico import IsMedico
from core.permissions.admin import IsAdmin
from core.permissions.paciente import IsPaciente

from rest_framework.permissions import IsAuthenticated

class MedicoViewSet(viewsets.ModelViewSet):
    queryset = Medico.objects.all()
    serializer_class = MedicoSerializer
    permission_classes = [IsAuthenticated, IsAdmin | IsMedico]

    def get_queryset(self):
        user = self.request.user
        if user.role == 'admin':
            return Medico.objects.all()
        elif user.role == 'medico':
            return Medico.objects.filter(user=user)
        elif user.role == 'paciente':
            return Medico.objects.none()