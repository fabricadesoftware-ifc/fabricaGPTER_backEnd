from rest_framework import serializers
from rest_framework.serializers import SlugRelatedField
from core.models.paciente import Paciente
from core.models.teste import Teste
from core.serializers.teste import TesteSerializer
from .user import UserSerializer, RegisterSerializer
from uploader.models import Image
from uploader.serializers import ImageSerializer


class PacienteSerializer(serializers.ModelSerializer):
    usuario = RegisterSerializer(write_only=True)
    usuario_info = UserSerializer(source='usuario', read_only=True)
    testes = TesteSerializer(many=True, read_only=True)

    class Meta:
        model = Paciente
        fields = [
            'id', 'usuario', 'usuario_info', 'endereco', 'numero', 'bairro', 'cidade', 'cep',
            'complemento', 'data_nascimento', 'mao_dominante', 'perfil', 'perfil_attachment_key', 'testes'
        ]

    def create(self, validated_data):
        usuario_data = validated_data.pop('usuario')
        usuario_serializer = RegisterSerializer(data=usuario_data)
        usuario_serializer.is_valid(raise_exception=True)
        usuario = usuario_serializer.save()
        paciente = Paciente.objects.create(usuario=usuario, **validated_data)
        return paciente

    def update(self, instance, validated_data):
        usuario_data = validated_data.pop('usuario', None)

        for field in ['endereco', 'numero', 'bairro', 'cidade', 'cep', 'complemento', 'data_nascimento', 'mao_dominante']:
            if field in validated_data:
                setattr(instance, field, validated_data[field])
        instance.save()

        if usuario_data:
            usuario = instance.usuario
            for key in ['nome', 'email', 'cpf']:
                if key in usuario_data:
                    setattr(usuario, key, usuario_data[key])
            if 'password' in usuario_data:
                usuario.set_password(usuario_data['password'])
            usuario.save()

        return instance

    perfil_attachment_key = SlugRelatedField(
        source="perfil",
        queryset=Image.objects.all(),
        slug_field="attachment_key",
        required=False,
        write_only=True,
    )
    perfil = ImageSerializer(required=False, read_only=True)
