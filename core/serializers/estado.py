from rest_framework import serializers
from core.models.estado import Estado

class EstadoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Estado
        fields = "__all__"