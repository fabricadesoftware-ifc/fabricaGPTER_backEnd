from django.db import models
from core.models.user import CustomUser

class Medico(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='medico_profile', blank=True, null=True)
    crm = models.CharField(max_length=20, blank=True, null=True)
    especialidade = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return f'{self.user}'