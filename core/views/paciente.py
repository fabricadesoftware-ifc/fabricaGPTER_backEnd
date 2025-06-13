from django.shortcuts import render
from rest_framework.viewsets import ModelViewSet

from core.models import Paciente
from core.serializers.paciente import PacienteSerializer


class PacienteViewSet(ModelViewSet):
    queryset = Paciente.objects.all()
    serializer_class = PacienteSerializer