from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from core.models import Profissional, Paciente
from core.serializers import ProfissionalSerializer, PacienteSerializer

class ProfissionalViewSet(viewsets.ModelViewSet):
    queryset = Profissional.objects.prefetch_related('pacientes').all()
    serializer_class = ProfissionalSerializer

    @action(detail=True, methods=['post'])
    def adicionar_pacientes(self, request, pk=None):
        """ add paciente a um profissional"""
        profissional = self.get_object()
        pacientes_ids = request.data.get('pacientes_ids', [])

        pacientes = Paciente.objects.filter(id__in=pacientes_ids)
        profissional.pacientes.add(*pacientes)

        serializer = self.get_serializer(profissional)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def remover_pacientes(self, request, pk=None):
        """ remove paciente de um profissional"""
        profissional = self.get_object()
        pacientes_ids = request.data.get('pacientes_ids', [])

        pacientes = Paciente.objects.filter(id__in=pacientes_ids)
        profissional.pacientes.remove(*pacientes)

        serializer = self.get_serializer(profissional)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def listar_pacientes(self, request, pk=None):
        """ lista pacientes associados a um profissional"""
        profissional = self.get_object()
        pacientes = profissional.pacientes.all()
        serializer = PacienteSerializer(pacientes, many=True)
        return Response(serializer.data)