from rest_framework import viewsets

from core.models.exame import Exame

from core.serializers.exame import ExameSerializer

from core.permissions.medico import IsMedico
from core.permissions.admin import IsAdmin
from core.permissions.paciente import IsPaciente

from rest_framework.permissions import IsAuthenticated

class ExameViewSet(viewsets.ModelViewSet):
    queryset = Exame.objects.all()
    serializer_class = ExameSerializer
    permission_classes = [IsAuthenticated, IsAdmin | IsMedico | IsPaciente]

    def get_queryset(self):
        user = self.request.user
        if user.role == 'admin':
            return Exame.objects.all()
        elif user.role == 'medico':
            return Exame.objects.filter(medico__user=user)
        elif user.role == 'paciente':
            return Exame.objects.filter(user=user)
        return Exame.objects.none()