from rest_framework import viewsets, permissions
from rest_framework.exceptions import PermissionDenied

from core.models.exame import Exame
from core.models.medico import Medico
from core.models.paciente import Paciente

from core.serializers.exame import ExameSerializer

from core.permissions.medico import IsMedico
from core.permissions.admin import IsAdmin
from core.permissions.paciente import IsPaciente

from rest_framework.permissions import IsAuthenticated

class ExameViewSet(viewsets.ModelViewSet):
    queryset = Exame.objects.all()
    serializer_class = ExameSerializer
    permission_classes = [IsAuthenticated, IsAdmin | IsPaciente]

    def get_queryset(self):
        user = self.request.user
        if user.role == 'admin':
            return Exame.objects.all()
        elif user.role == 'medico':
            return Exame.objects.none()
        elif user.role == 'paciente':
            return Exame.objects.filter(paciente__user=user)
        return Exame.objects.none()
    
    #def perform_create(self, serializer):
     #   user = self.request.user

    #try:
     #   medico = Medico.objects.get(user=user)
    #except Medico.DoesNotExist:
     #   raise PermissionDenied("Você não é um médico válido.")

    #paciente = serializer.validated_data.get('paciente')

    #if paciente.medico != medico:
     #   raise PermissionDenied("Você não tem permissão para criar exames para esse paciente.")

    #serializer.save()