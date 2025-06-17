from django.db import models
from core.models.user import CustomUser
from core.models.medico import Medico


class Paciente(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='paciente_profile', blank=True, null=True)
    medico = models.ForeignKey(Medico, on_delete=models.CASCADE, related_name='pacientes', blank=True, null=True)
    data_nascimento = models.DateField(
        ("Data de Nascimento"), auto_now=False, auto_now_add=False, blank=True, null=True
    )
    endereco = models.CharField(max_length=200, blank=True, null=True)

    def __str__(self):
        return f'{self.user}'