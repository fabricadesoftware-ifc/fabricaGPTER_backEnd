from django.conf import settings
from django.db import models


class AccessProfile(models.Model):
    class Role(models.TextChoices):
        PATIENT = 'paciente', 'Paciente'
        PROFESSIONAL = 'profissional', 'Profissional'

    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
                               related_name='access_profile')
    role = models.CharField(max_length=12, choices=Role.choices)

    class Meta:
        constraints = [models.CheckConstraint(
            condition=models.Q(role__in=['paciente', 'profissional']),
            name='accounts_valid_role',
        )]

    def __str__(self):
        return f'{self.user} — {self.get_role_display()}'
