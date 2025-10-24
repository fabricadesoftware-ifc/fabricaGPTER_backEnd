from rest_framework import serializers
from core.models.exame import Exame

class ExameSerializer(serializers.ModelSerializer):
    class Meta:
        model = Exame
        fields = '__all__'
        read_only_fields = ('usuario',)  
