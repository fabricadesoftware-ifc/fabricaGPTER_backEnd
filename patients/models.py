from django.conf import settings
from django.db import models
from django.db.models.functions import Lower


class Patient(models.Model):
    class Status(models.TextChoices):
        ACTIVE = 'ativo', 'Ativo'
        INACTIVE = 'inativo', 'Inativo'

    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
                                related_name='patient')
    professional = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT,
                                     related_name='patients')
    name = models.CharField(max_length=150)
    email = models.EmailField(max_length=254)
    cpf = models.CharField(max_length=11, unique=True)
    cep = models.CharField(max_length=8)
    street = models.CharField(max_length=255)
    city = models.CharField(max_length=255)
    state = models.CharField(max_length=2)
    neighborhood = models.CharField(max_length=255)
    number = models.CharField(max_length=20)
    phone = models.CharField(max_length=20, null=True, blank=True)
    birth_date = models.DateField(null=True, blank=True)
    photo = models.CharField(max_length=500, null=True, blank=True)
    status = models.CharField(max_length=8, choices=Status.choices, default=Status.ACTIVE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ('name', 'id')
        constraints = [
            models.CheckConstraint(
                condition=models.Q(status__in=['ativo', 'inativo']),
                name='patients_valid_status',
            ),
            models.UniqueConstraint(Lower('email'), name='patients_unique_email'),
        ]
        indexes = [
            models.Index(fields=('professional', 'name'), name='patients_prof_name_idx'),
        ]

    def __str__(self):
        return f'{self.name} ({self.user.get_username()})'

    @property
    def address(self):
        cep = f'{self.cep[:5]}-{self.cep[5:]}' if len(self.cep) == 8 else self.cep
        return (f'{self.street}, {self.number} - {self.neighborhood}, '
                f'{self.city} - {self.state}, CEP {cep}')
