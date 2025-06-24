from django.db import models

from core.models.paciente import Paciente

class Exame(models.Model):
    data = models.DateTimeField(
        ("Data do Exame"), auto_now=False, auto_now_add=False, blank=True, null=True
    )
    paciente = models.ForeignKey(Paciente, on_delete=models.CASCADE, related_name='exames', blank=True, null=True)
    forca = models.DecimalField("Força (N)", max_digits=5, decimal_places=1, null=True, blank=True)
    descricao = models.CharField(max_length=100, blank=True, null=True)
    