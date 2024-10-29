from django.db import models


class Patient(models.Model):
    name = models.CharField(max_length=100)
    cpf = models.CharField(max_length=14, unique=True)
    email = models.EmailField(unique=True)
    birth_date = models.DateField()
    gender = models.CharField(max_length=1, choices=[("M", "Male"), ("F", "Female")])

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Paciente"
        verbose_name_plural = "Pacientes"
