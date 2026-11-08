from django.conf import settings
from django.db import models


class ProfessionalProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
                                related_name='professional_profile',
                                verbose_name='usuário')
    phone = models.CharField('telefone', max_length=20, blank=True, null=True)
    birth_date = models.DateField('data de nascimento', blank=True, null=True)
    cpf = models.CharField('CPF', max_length=11, unique=True, blank=True, null=True)
    photo = models.CharField('foto', max_length=500, blank=True, null=True)

    class Meta:
        verbose_name = 'informações do profissional'
        verbose_name_plural = 'informações dos profissionais'

    def __str__(self):
        return f'Informações profissionais — {self.user}'


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
