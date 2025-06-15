from rest_framework.serializers import CharField, ModelSerializer, SerializerMethodField

from core.models import Paciente

class PacienteSerializer(ModelSerializer):
    class Meta:
        model = Paciente
        fields = '__all__'