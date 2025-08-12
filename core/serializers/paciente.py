from rest_framework import serializers
from core.models.paciente import Paciente


class PacienteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Paciente
        fields = '__all__'
        read_only_fields = ('usuario',)  

    