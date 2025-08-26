from django.db import models
from .clinica import Clinica
from .user import UsuarioBase

class Profissional(models.Model):
    usuario = models.OneToOneField(UsuarioBase, on_delete=models.PROTECT)
    cpf = models.CharField(max_length=11, unique=True)
    matricula = models.CharField(max_length=300)
    telefone = models.CharField(max_length=20)
    data_nascimento = models.DateField()
    clinica = models.ForeignKey(Clinica, on_delete=models.PROTECT)

    def __str__(self):
        return self.usuario.username