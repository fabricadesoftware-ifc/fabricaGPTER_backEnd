from django.db import models

from core.models.medico import Medico;

class Paciente(models.Model):
    nome = models.CharField(max_length=255)
    email = models.EmailField(null=True, blank=True)
    telefone = models.CharField(max_length=255)
    medico = models.ForeignKey(Medico, on_delete=models.PROTECT, related_name="pacientes", blank=True, null=True)

    def __str__(self):
        return self.nome