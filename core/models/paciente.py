from django.contrib.auth.models import Group
from django.db import models
from .clinica import Clinica
from .user import UsuarioBase

class Paciente(models.Model):
    usuario = models.OneToOneField(UsuarioBase, on_delete=models.PROTECT)
    cpf = models.CharField(max_length=11, unique=True)
    endereco = models.CharField(max_length=150)
    numero = models.IntegerField()
    bairro = models.CharField(max_length=100)
    cidade = models.CharField(max_length=150)
    cep = models.CharField(max_length=10)
    complemento = models.CharField(max_length=200, blank=True, null=True)
    data_nascimento = models.DateField()
    clinica = models.ForeignKey(Clinica, on_delete=models.PROTECT)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        grupo, created = Group.objects.get_or_create(name="pacientes")
        self.usuario.groups.add(grupo)

    def __str__(self):
        return self.usuario.username