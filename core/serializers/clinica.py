from rest_framework import serializers
from core.models.clinica import Clinica

class ClinicaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Clinica
        fields = "__all__"