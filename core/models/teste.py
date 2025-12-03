from django.db import models
from .paciente import Paciente

class Teste(models.Model):
    paciente = models.ForeignKey(Paciente, on_delete=models.PROTECT, related_name='testes')
    forca =  models.IntegerField()
    tempo = models.IntegerField()
    data = models.DateField(blank=True, auto_now_add=True)
    detalhes = models.CharField(max_length=150, blank=True)

    def __str__(self):
        return self.paciente.usuario.username