from django.db import models

class Estado(models.Model):
    cod_IBGE = models.IntegerField(null=True, blank=True)
    nome = models.CharField(max_length=200, blank=True, null=True)
    sigla = models.CharField(max_length=2, blank=True, null=True)

    def __str__(self):
        return f'{self.nome} ({self.sigla})'