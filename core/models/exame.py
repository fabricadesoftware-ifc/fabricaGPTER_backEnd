from django.db import models
from .user import UsuarioBase

class Exame(models.Model):
    forca =  models.IntegerField(unique=True)
    tempo = models.IntegerField(unique=True)
    data = models.DateField(blank=True)
    usuario = models.OneToOneField(UsuarioBase, on_delete=models.PROTECT)

    def __str__(self):
        return self.usuario.username