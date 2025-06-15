from django.db import models

class Medico(models.Model):
    nome = models.CharField(max_length=255)
    email = models.EmailField(null=True, blank=True)
    telefone = models.CharField(max_length=255)

    def _str_(self):
        return self.nome