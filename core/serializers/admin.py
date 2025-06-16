from rest_framework.serializers import CharField, ModelSerializer, SerializerMethodField

from core.models import Admin

class AdminSerializer(ModelSerializer):
    class Meta:
        model = Admin
        fields = '__all__'