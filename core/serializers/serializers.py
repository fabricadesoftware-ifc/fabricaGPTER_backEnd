# from rest_framework import serializers
# from core.models.models import CustomUser, Medico, Paciente


# class UserSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = CustomUser
#         fields = ['id', 'username', 'email', 'role', 'first_name', 'last_name']


# class MedicoSerializer(serializers.ModelSerializer):
#     user = UserSerializer()

#     class Meta:
#         model = Medico
#         fields = ['id', 'user', 'crm', 'especialidade']


# class PacienteSerializer(serializers.ModelSerializer):
#     user = UserSerializer()
#     medico = serializers.PrimaryKeyRelatedField(queryset=Medico.objects.all())

#     class Meta:
#         model = Paciente
#         fields = ['id', 'user', 'medico', 'data_nascimento', 'endereco']