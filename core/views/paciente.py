from rest_framework import viewsets
from core.models.paciente import Paciente
from core.serializers.paciente import PacienteSerializer

class PacienteViewSet(viewsets.ModelViewSet):
    queryset = Paciente.objects.all()
    serializer_class = PacienteSerializer
    


