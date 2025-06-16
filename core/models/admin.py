from django.db import models

class Admin(models.Model):
    nome = models.CharField(max_length=255)
    email = models.EmailField(max_length=255)
    telefone = models.CharField(max_length=255)

    def __str__(self):
        return self.nome