from rest_framework.viewsets import ModelViewSet

from core.models import Handgrip
from core.serializers import HandGripSerializer

class PatientViewSet(ModelViewSet):
    queryset = Handgrip.objects.all()
    serializer_class = HandGripSerializer