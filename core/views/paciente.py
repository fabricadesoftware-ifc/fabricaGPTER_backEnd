from rest_framework import viewsets

from rest_framework.permissions import IsAuthenticated

from core.models.paciente import Paciente
from core.serializers.paciente import PacienteSerializer

class PacienteViewSet(viewsets.ModelViewSet):
    queryset = Paciente.objects.all()
    serializer_class = PacienteSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user

        if hasattr(user, "administrador"):
            return Paciente.objects.all()

        if hasattr(user, "funcionario"):
            return Paciente.objects.filter(medico=user.funcionario)

        if hasattr(user, "paciente"):
            return Paciente.objects.filter(usuario=user)

        return Paciente.objects.none()

    def perform_create(self, serializer):
        user = self.request.user

        if hasattr(user, "funcionario"):
            serializer.save(medico=user.funcionario)

        elif hasattr(user, "administrador"):
            serializer.save(
                medico=serializer.validated_data.get("medico"),
                usuario=serializer.validated_data.get("usuario")
            )

        else:
            raise PermissionError("Você não tem permissão para criar pacientes.")

    


