from rest_framework import serializers
from core.models.paciente import Paciente
from .user import UsuarioBaseSerializer


class PacienteSerializer(serializers.ModelSerializer):
    usuario = UsuarioBaseSerializer()

    class Meta:
        model = Paciente
        fields = '__all__'
        read_only_fields = ('usuario',)  

    