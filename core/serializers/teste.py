from rest_framework import serializers
from core.models.teste import Teste

class TesteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Teste
        fields = '__all__'
        read_only_fields = ('usuario',)  

    def create(self, validated_data):
        request = self.context.get('request')
        validated_data['usuario'] = request.user
        return super().create(validated_data)