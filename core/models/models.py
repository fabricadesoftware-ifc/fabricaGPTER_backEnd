# from django.contrib.auth.models import AbstractUser
# from django.db import models


# class CustomUser(AbstractUser):
#     ROLE_CHOICES = (
#         ('admin', 'Administrador'),
#         ('medico', 'Médico'),
#         ('paciente', 'Paciente'),
#     )
#     role = models.CharField(max_length=10, choices=ROLE_CHOICES)


# class Medico(models.Model):
#     user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='medico_profile', blank=True, null=True)
#     crm = models.CharField(max_length=20, blank=True, null=True)
#     especialidade = models.CharField(max_length=100, blank=True, null=True)

#     def __str__(self):
#         return f'{self.user}'


# class Paciente(models.Model):
#     user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='paciente_profile', blank=True, null=True)
#     medico = models.ForeignKey(Medico, on_delete=models.CASCADE, related_name='pacientes', blank=True, null=True)
#     data_nascimento = models.DateField(
#         ("Data de Nascimento"), auto_now=False, auto_now_add=False, blank=True, null=True
#     )
#     endereco = models.CharField(max_length=200, blank=True, null=True)

#     def __str__(self):
#         return f'{self.user}'