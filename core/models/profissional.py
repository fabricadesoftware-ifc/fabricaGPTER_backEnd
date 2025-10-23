from django.db import models
from .user import UsuarioBase

class Profissional(models.Model):
    usuario = models.OneToOneField(UsuarioBase, on_delete=models.PROTECT)
    cpf = models.CharField(max_length=11, unique=True)
    telefone = models.CharField(max_length=20)
    data_nascimento = models.DateField()

    def __str__(self):
        return self.usuario.username