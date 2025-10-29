from rest_framework import serializers
from core.models.paciente import Paciente

from core.models.teste import Teste
from core.serializers.teste import TesteSerializer


class PacienteSerializer(serializers.ModelSerializer):
    testes = TesteSerializer(many=True, read_only=True)
    
    class Meta:
        model = Paciente
        fields = '__all__'
        read_only_fields = ('usuario',)  

    