from rest_framework import serializers
from core.models.paciente import Paciente

class PacienteSerializer(serializers.ModelSerializer):
    profissional = serializers.PrimaryKeyRelatedField(read_only=True)
    usuario = serializers.PrimaryKeyRelatedField(
        queryset=Paciente._meta.get_field('usuario').related_model.objects.all()
    )

    class Meta:
        model = Paciente
        fields = "__all__"