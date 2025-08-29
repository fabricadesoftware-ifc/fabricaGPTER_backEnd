from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from core.models.paciente import Paciente
from core.serializers.paciente import PacienteSerializer
from core.permissions.permissions import IsAdminOrProfissional

class PacienteViewSet(viewsets.ModelViewSet):
    queryset = Paciente.objects.all()
    serializer_class = PacienteSerializer
    permission_classes = [IsAuthenticated, IsAdminOrProfissional]

    def get_queryset(self):
        user = self.request.user

        if hasattr(user, "administrador"):
            return Paciente.objects.all()

        if hasattr(user, "profissional"):
            return Paciente.objects.filter(profissional=user.profissional)

        if hasattr(user, "paciente"):
            return Paciente.objects.filter(usuario=user)

        return Paciente.objects.none()

    def perform_create(self, serializer):
        user = self.request.user

        if hasattr(user, "profissional"):
            serializer.save(profissional=user.profissional)

        elif hasattr(user, "administrador"):
            serializer.save(
                profissional=serializer.validated_data.get("profissional"),
                usuario=serializer.validated_data.get("usuario")
            )

        else:
            raise PermissionError("Você não tem permissão para criar pacientes.")