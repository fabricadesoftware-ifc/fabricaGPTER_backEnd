from rest_framework import serializers
from core.models.paciente import Paciente
from core.models.medico import Medico

from core.serializers.user import UserSerializer
#from core.serializers.medico import MedicoSerializer

class PacienteSerializer(serializers.ModelSerializer):
    user = UserSerializer()
    medico = serializers.PrimaryKeyRelatedField(queryset=Medico.objects.all())

    class Meta:
        model = Paciente
        fields = ['id', 'user', 'medico', 'data_nascimento', 'endereco']