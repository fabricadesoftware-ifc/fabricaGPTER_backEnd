from rest_framework.serializers import CharField, ModelSerializer, SerializerMethodField

from core.models import Medico

class MedicoSerializer(ModelSerializer):
    class Meta:
        model = Medico
        fields = "_all_"