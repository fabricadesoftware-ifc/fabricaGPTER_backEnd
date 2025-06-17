from rest_framework import serializers
from core.models.medico import Medico

from core.serializers.user import UserSerializer

class MedicoSerializer(serializers.ModelSerializer):
    user = UserSerializer()

    class Meta:
        model = Medico
        fields = ['id', 'user', 'crm', 'especialidade']