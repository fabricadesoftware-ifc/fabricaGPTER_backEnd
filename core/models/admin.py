from django.db import models
from .user import UsuarioBase

class Administrador(models.Model):
    usuario = models.OneToOneField(UsuarioBase, on_delete=models.CASCADE)
    cpf = models.CharField(max_length=11, unique=True)

    def __str__(self):
        return self.usuario.username