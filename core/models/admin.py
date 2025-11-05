from django.db import models
from .user import UsuarioBase

class Administrador(models.Model):
    usuario = models.OneToOneField(UsuarioBase, on_delete=models.PROTECT)
    def __str__(self):
        return self.usuario.username