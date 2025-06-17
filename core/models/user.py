from django.contrib.auth.models import AbstractUser
from django.db import models


class CustomUser(AbstractUser):
    ROLE_CHOICES = (
        ('admin', 'Administrador'),
        ('medico', 'Médico'),
        ('paciente', 'Paciente'),
    )
    role = models.CharField(max_length=10, choices=ROLE_CHOICES)