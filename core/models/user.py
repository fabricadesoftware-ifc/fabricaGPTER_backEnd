from django.contrib.auth.models import AbstractUser
from django.db import models

class UsuarioBase(AbstractUser):
    nome = models.CharField(max_length=150)
    email = models.EmailField(unique=True)
    cpf = models.CharField(max_length=11, unique=True, null=True, blank=True)
    is_admin = models.BooleanField(default=False)
    