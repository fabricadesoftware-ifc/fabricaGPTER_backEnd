from rest_framework import viewsets

from core.models.clinica import Clinica
from core.serializers.clinica import ClinicaSerializer

class ClinicaViewSet(viewsets.ModelViewSet):
    queryset = Clinica.objects.all()
    serializer_class = ClinicaSerializer