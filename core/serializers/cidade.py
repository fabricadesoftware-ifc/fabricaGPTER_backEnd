from rest_framework import serializers
from core.models.cidade import Cidade

class CidadeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cidade
        fields = "__all__"