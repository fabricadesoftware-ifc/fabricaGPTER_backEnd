from rest_framework import serializers
from core.models import UsuarioBase

class UsuarioBaseSerializer(serializers.ModelSerializer):
    senha = serializers.CharField(write_only=True, required=True)
    
    class Meta:
        model = UsuarioBase
        fields = ['id', 'nome', 'email', 'cpf', 'senha', 'is_admin']
        extra_kwargs = {
            'senha': {'write_only': True}
        }
    
    def create(self, validated_data):
        senha = validated_data.pop('senha')
        email = validated_data.get('email')
        usuario = UsuarioBase(
            username=email,  
            **validated_data
        )
        usuario.set_password(senha)
        usuario.save()
        return usuario
    
    def update(self, instance, validated_data):
        senha = validated_data.pop('senha', None)
        
        if 'email' in validated_data:
            instance.username = validated_data['email']
        
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        
        if senha:
            instance.set_password(senha)
        
        instance.save()
        return instance
