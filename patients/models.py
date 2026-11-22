from django.conf import settings
from django.db import models
from django.db.models.functions import Lower


class Patient(models.Model):
    class DominantHand(models.TextChoices):
        RIGHT = 'Direita', 'Direita'
        LEFT = 'Esquerda', 'Esquerda'

    class Status(models.TextChoices):
        ACTIVE = 'ativo', 'Ativo'
        INACTIVE = 'inativo', 'Inativo'

    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
                                related_name='patient', null=True, blank=True)
    professional = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT,
                                     related_name='patients', null=True, blank=True)
    name = models.CharField(max_length=150)
    email = models.EmailField(max_length=254)
    cpf = models.CharField(max_length=11, unique=True)
    cep = models.CharField(max_length=8)
    street = models.CharField(max_length=255)
    city = models.CharField(max_length=255)
    state = models.CharField(max_length=2)
    neighborhood = models.CharField(max_length=255)
    number = models.CharField(max_length=20)
    dominant_hand = models.CharField(max_length=8, choices=DominantHand.choices, null=True)
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
                condition=(models.Q(dominant_hand__in=['Direita', 'Esquerda'])
                           | models.Q(dominant_hand__isnull=True)),
                name='patients_valid_dominant_hand',
            ),
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
        return f'{self.name} ({self.user.get_username()})' if self.user_id else self.name

    @property
    def address(self):
        cep = f'{self.cep[:5]}-{self.cep[5:]}' if len(self.cep) == 8 else self.cep
        return (f'{self.street}, {self.number} - {self.neighborhood}, '
                f'{self.city} - {self.state}, CEP {cep}')


class Assessment(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.PROTECT, related_name='assessments')
    observations = models.TextField(blank=True, default='')

    # A test is uploaded and retrieved as one ordered series.
    measurements = models.JSONField(default=list, blank=True)
    seconds = models.PositiveSmallIntegerField(choices=[(n, str(n)) for n in (30, 60, 120)], null=True)
    arm = models.CharField(max_length=8, choices=Patient.DominantHand.choices, blank=True)
    status = models.CharField(max_length=9, null=True, default='running', choices=[
        ('running', 'Em andamento'), ('finished', 'Finalizado'),
        ('validated', 'Validado'), ('cancelled', 'Cancelado'),
    ])
    date = models.DateField(null=True, editable=False)
