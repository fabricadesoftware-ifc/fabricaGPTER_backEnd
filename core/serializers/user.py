from rest_framework import serializers
from core.models.user import UsuarioBase

class UsuarioBaseSerializer(serializers.ModelSerializer):
    class Meta:
        model = UsuarioBase
        fields = ['id', 'nome', 'email', 'cpf', 'is_admin']
        extra_kwargs = {'senha': {'write_only': True}}
    
    def create(self, validated_data):
        senha = validated_data.pop('senha', None)
        usuario = UsuarioBase(**validated_data)
        if senha:
            usuario.set_password(senha)
        usuario.save()
        return usuario
