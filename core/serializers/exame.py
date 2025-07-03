from rest_framework import serializers

from core.models.exame import Exame
from core.models.paciente import Paciente
from core.serializers.paciente import PacienteSerializer

class ExameSerializer(serializers.ModelSerializer):
    paciente = serializers.PrimaryKeyRelatedField(queryset=Paciente.objects.all())

    class Meta:
        model = Exame
        fields = ['id', 'paciente', 'data', 'forca', 'descricao']
        