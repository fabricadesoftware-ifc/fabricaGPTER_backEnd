from django.db import models
from .user import UsuarioBase
from django.contrib.auth.models import Group

class Administrador(models.Model):
    usuario = models.OneToOneField(UsuarioBase, on_delete=models.CASCADE)
    cpf = models.CharField(max_length=11, unique=True)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        grupo, created = Group.objects.get_or_create(name="administradores")
        self.usuario.groups.add(grupo)

    def __str__(self):
        return self.usuario.username
    
    