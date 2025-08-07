from django.db import models
from core.models.cidade import Cidade

class Clinica(models.Model):
    endereco = models.CharField(max_length=255, blank=True, null=True)
    numero = models.IntegerField(blank=True, null=True)
    bairro = models.CharField(max_length=50, blank=True, null=True)
    cidade = models.ForeignKey(Cidade, on_delete=models.PROTECT, blank=True, null=True)
    cep = models.IntegerField()
    cnpj = models.CharField(max_length=100, blank=True, null=True)
    razao_social = models.CharField(max_length=150, blank=True, null=True)
    nome_fantasia = models.CharField(max_length=150, blank=True, null=True)

    def __str__(self):
        return f'{self.nome_fantasia or self.razao_social}'