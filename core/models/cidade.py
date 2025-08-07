from django.db import models
from core.models.estado import Estado

class Cidade(models.Model):
    cod_IBGE = models.IntegerField(null=True, blank=True)
    nome = models.CharField(max_length=200, blank=True, null=True)
    estado = models.ForeignKey(Estado, on_delete=models.PROTECT, null=True, blank=True)

    def __str__(self):
        return f'{self.nome} ({self.sigla})'