from rest_framework import serializers
from core.models.admin import Administrador

class AdministradorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Administrador
        fields = '__all__'
        read_only_fields = ('usuario',)  
