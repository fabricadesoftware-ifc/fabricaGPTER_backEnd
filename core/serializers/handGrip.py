from rest_framework.serializers import ModelSerializer

from core.models import Handgrip

class HandGripSerializer(ModelSerializer):
    class Meta:
        model = Handgrip
        fields = "__all__"