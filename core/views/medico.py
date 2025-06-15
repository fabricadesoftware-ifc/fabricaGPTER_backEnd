from django.shortcuts import render
from rest_framework.viewsets import ModelViewSet

from core.models import Medico
from core.serializers.medico import MedicoSerializer


class MedicoViewSet(ModelViewSet):
    queryset = Medico.objects.all()
    serializer_class = MedicoSerializer