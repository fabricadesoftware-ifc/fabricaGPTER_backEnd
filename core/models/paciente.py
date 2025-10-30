from django.db import models
from .user import UsuarioBase

class Paciente(models.Model):
    usuario = models.OneToOneField(UsuarioBase, on_delete=models.PROTECT)
    endereco = models.CharField(max_length=150)
    numero = models.IntegerField()
    bairro = models.CharField(max_length=100)
    cidade = models.CharField(max_length=150)
    cep = models.CharField(max_length=10)
    complemento = models.CharField(max_length=200, blank=True, null=True)
    data_nascimento = models.DateField()
    class MaoDominante(models.TextChoices):
        DESTRO = 'destro', 'Destro'
        AMBIDESTRO = 'ambidestro', 'Ambidestro'
        CANHOTO = 'canhoto', 'Canhoto'

    mao_dominante = models.CharField(max_length=10, choices=MaoDominante.choices, default=MaoDominante.DESTRO)

    def __str__(self):
        return self.usuario.username