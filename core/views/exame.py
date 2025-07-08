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
from rest_framework.decorators import action
from rest_framework.response import Response

class ExameViewSet(viewsets.ModelViewSet):
    queryset = Exame.objects.all()
    serializer_class = ExameSerializer
    permission_classes = [IsAuthenticated, IsAdmin | IsPaciente]

    def get_queryset(self):
        user = self.request.user
        paciente_id = self.kwargs.get('paciente_id')

        if user.role == 'admin':
            if paciente_id:
                return Exame.objects.filter(paciente_id=paciente_id)
            return Exame.objects.all()

        if user.role == 'medico':
            return Exame.objects.none()
        
        if user.role == 'paciente':
            if paciente_id:
                if int(paciente_id) != user.paciente.id:
                    return Exame.objects.none()
                return Exame.objects.filter(paciente_id=paciente_id)
            return Exame.objects.filter(paciente__user=user)

        return Exame.objects.none()

    def perform_create(self, serializer):
        paciente_id = self.kwargs.get('paciente_id')
        serializer.save(paciente_id=paciente_id)

    @action(detail=False, methods=['get', 'post'], url_path='pacientes/(?P<paciente_id>[^/.]+)/exames')
    def exames_por_paciente(self, request, paciente_id=None):
        if request.method == 'GET':
            queryset = self.get_queryset().filter(paciente_id=paciente_id)
            serializer = self.get_serializer(queryset, many=True)
            return Response(serializer.data)

        if request.method == 'POST':
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save(paciente_id=paciente_id)
            return Response(serializer.data, status=201)
