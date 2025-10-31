from django.db import models
from .user import UsuarioBase
from .paciente import Paciente
from django.utils import timezone

class Profissional(models.Model):
    usuario = models.OneToOneField(UsuarioBase, on_delete=models.PROTECT)
    telefone = models.CharField(max_length=20)
    pacientes = models.ManyToManyField(Paciente, through='ProfissionalPaciente', related_name='profissionais', blank=True)



    def __str__(self):
        return self.usuario.username

class ProfissionalPaciente(models.Model):
    profissional = models.ForeignKey(Profissional, on_delete=models.PROTECT)
    paciente = models.ForeignKey(Paciente, on_delete=models.PROTECT)
    data_atendimento = models.DateField(default=timezone.now)
    observacoes = models.TextField(blank=True, null=True)
    ativo = models.BooleanField(default=True)

    class Meta:
        unique_together = ('profissional', 'paciente')
        verbose_name = 'Relacionamento Profissional-Paciente'
        verbose_name_plural = 'Relacionamentos Profissional-Paciente'
