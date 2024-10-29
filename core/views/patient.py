from rest_framework.viewsets import ModelViewSet

from core.models import Patient
from core.serializers import PatientSerializer

class PatientViewSet(ModelViewSet):
    queryset = Patient.objects.all()
    serializer_class = PatientSerializer