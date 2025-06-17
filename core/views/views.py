# from rest_framework import viewsets
# from core.models.models import Medico, Paciente
# from core.serializers.serializers import MedicoSerializer, PacienteSerializer
# from core.permissions.permissions import IsMedico, IsAdmin, IsPaciente
# from rest_framework.permissions import IsAuthenticated


# class MedicoViewSet(viewsets.ModelViewSet):
#     queryset = Medico.objects.all()
#     serializer_class = MedicoSerializer
#     permission_classes = [IsAuthenticated, IsAdmin]


# class PacienteViewSet(viewsets.ModelViewSet):
#     queryset = Paciente.objects.all()
#     serializer_class = PacienteSerializer
#     permission_classes = [IsAuthenticated, IsMedico | IsAdmin | IsPaciente]

#     def get_queryset(self):
#         user = self.request.user
#         if user.role == 'admin':
#             return Paciente.objects.all()
#         elif user.role == 'medico':
#             return Paciente.objects.filter(medico__user=user)
#         elif user.role == 'paciente':
#             return Paciente.objects.filter(user=user)
#         return Paciente.objects.none()