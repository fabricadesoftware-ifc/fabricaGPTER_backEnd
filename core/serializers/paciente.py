from rest_framework import serializers
from core.models import Paciente
from .user import UsuarioBaseSerializer

class PacienteSerializer(serializers.ModelSerializer):
    usuario = UsuarioBaseSerializer()
    
    class Meta:
        model = Paciente
        fields = '__all__'
    
    def create(self, validated_data):
        usuario_data = validated_data.pop('usuario')
        usuario_serializer = UsuarioBaseSerializer(data=usuario_data)
        usuario_serializer.is_valid(raise_exception=True)
        usuario = usuario_serializer.save()
  
        paciente = Paciente.objects.create(usuario=usuario, **validated_data)
        return paciente
    
    def update(self, instance, validated_data):
        
        usuario_data = validated_data.pop('usuario', None)
     
        instance.endereco = validated_data.get('endereco', instance.endereco)
        instance.numero = validated_data.get('numero', instance.numero)
        instance.bairro = validated_data.get('bairro', instance.bairro)
        instance.cidade = validated_data.get('cidade', instance.cidade)
        instance.cep = validated_data.get('cep', instance.cep)
        instance.complemento = validated_data.get('complemento', instance.complemento)
        instance.data_nascimento = validated_data.get('data_nascimento', instance.data_nascimento)
        instance.mao_dominante = validated_data.get('mao_dominante', instance.mao_dominante)
        instance.save()

        if usuario_data:
            usuario = instance.usuario
            usuario.nome = usuario_data.get('nome', usuario.nome)
            usuario.email = usuario_data.get('email', usuario.email)
            usuario.cpf = usuario_data.get('cpf', usuario.cpf)
            if 'senha' in usuario_data:
                usuario.set_password(usuario_data['senha'])
            usuario.save()
        
        return instance
