from rest_framework import serializers
from core.models import Profissional, Paciente
from .user import UserSerializer
from .paciente import PacienteSerializer

class ProfissionalSerializer(serializers.ModelSerializer):
    usuario = UserSerializer()

    pacientes_ids = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Paciente.objects.all(),
        source='pacientes',
        write_only=True,
        required=False
    )
    pacientes = PacienteSerializer(many=True, read_only=True)

    class Meta:
        model = Profissional
        fields = ['id', 'usuario', 'telefone', 'pacientes', 'pacientes_ids']

    def create(self, validated_data):
        usuario_data = validated_data.pop('usuario')
        pacientes_data = validated_data.pop('pacientes', [])

        usuario_serializer = UserSerializer(data=usuario_data)
        usuario_serializer.is_valid(raise_exception=True)
        usuario = usuario_serializer.save()

        profissional = Profissional.objects.create(usuario=usuario, **validated_data)

        if pacientes_data:
            profissional.pacientes.set(pacientes_data)

        return profissional

        def update(self, instance, validated_data):
            usuario_data = validated_data.pop('usuario', None)
            pacientes_data = validated_data.pop('pacientes', None)

            for attr, value in validated_data.items():
                setattr(instance, attr, value)
            instance.save()

            if usuario_data:
                usuario = instance.usuario
                for attr, value in usuario_data.items():
                    setattr(usuario, attr, value)
                usuario.save()

            if pacientes_data is not None:
                instance.pacientes.set(pacientes_data)

            return instance