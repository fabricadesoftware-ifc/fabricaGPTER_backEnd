from rest_framework import generics
from core.serializers.user import RegisterSerializer, UserSerializer
from django.contrib.auth import get_user_model

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from core.serializers.paciente import PacienteSerializer
from core.serializers.profissional import ProfissionalSerializer
from core.serializers.admin import AdministradorSerializer
from core.models.admin import Administrador

User = get_user_model()

class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = RegisterSerializer

class RegisterPacienteView(generics.CreateAPIView):
    serializer_class = PacienteSerializer

    def get_queryset(self):
        return User.objects.all()

class RegisterProfissionalView(generics.CreateAPIView):
    serializer_class = ProfissionalSerializer

    def get_queryset(self):
        return User.objects.all()

class RegisterAdministradorView(generics.CreateAPIView):
    serializer_class = AdministradorSerializer

    def create(self, request, *args, **kwargs):
        usuario_data = request.data.get('usuario')
        if not usuario_data:
            return Response({"usuario": ["Este campo é obrigatório."]}, status=400)
        user_serializer = RegisterSerializer(data=usuario_data)
        user_serializer.is_valid(raise_exception=True)
        user = user_serializer.save()
        admin = Administrador.objects.create(usuario=user)
        serializer = AdministradorSerializer(admin)
        return Response(serializer.data, status=201)

class MeView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = UserSerializer(request.user)
        data = serializer.data
        perfil = None
        if hasattr(request.user, 'paciente'):
            perfil = 'paciente'
        elif hasattr(request.user, 'profissional'):
            perfil = 'profissional'
        elif hasattr(request.user, 'administrador'):
            perfil = 'administrador'
        data['perfil_tipo'] = perfil
        return Response(data)