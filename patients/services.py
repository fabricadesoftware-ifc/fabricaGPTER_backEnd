from django.contrib.auth import get_user_model
from django.contrib.sessions.models import Session
from django.db import transaction
from django.utils import timezone

from accounts.models import AccessProfile

from .models import Patient

User = get_user_model()

PATIENT_FIELDS = (
    'name', 'email', 'cpf', 'cep', 'street', 'city', 'state', 'neighborhood',
    'number', 'phone', 'photo', 'dominant_hand',
)


def create_patient_account(*, professional, data):
    """Create the account and the patient record atomically."""
    with transaction.atomic():
        user = User(username=data['username'], email=data['email'],
                    first_name=data['name'])
        user.set_password(data['password'])
        user.save()
        AccessProfile.objects.create(user=user, role=AccessProfile.Role.PATIENT)
        return create_patient_record(data, user=user, professional=professional)


def create_patient_record(data, *, user=None, professional=None):
    fields = {field: data[field] for field in PATIENT_FIELDS if field in data}
    return Patient.objects.create(user=user, professional=professional,
                                  birth_date=data.get('birthDate'), **fields)


def update_patient(patient, data):
    with transaction.atomic():
        user = patient.user
        user_fields = []
        if user and 'username' in data:
            user.username = data['username']
            user_fields.append('username')
        if user and 'name' in data:
            user.first_name = data['name']
            user_fields.append('first_name')
        if user and 'email' in data:
            user.email = data['email']
            user_fields.append('email')
        if user_fields:
            user.save(update_fields=user_fields)

        patient_fields = []
        mapping = {'birthDate': 'birth_date'}
        for field in PATIENT_FIELDS + ('birthDate',):
            if field in data:
                setattr(patient, mapping.get(field, field), data[field])
                patient_fields.append(mapping.get(field, field))
        if patient_fields:
            patient.save(update_fields=patient_fields + ['updated_at'])
    return patient


def deactivate_patient(patient):
    """Soft-delete: disable the patient access without cascading related data."""
    with transaction.atomic():
        if patient.status != Patient.Status.INACTIVE:
            patient.status = Patient.Status.INACTIVE
            patient.save(update_fields=['status', 'updated_at'])
        user = patient.user
        if user is None:
            return patient
        if user.is_active:
            user.is_active = False
            user.save(update_fields=['is_active'])
        delete_user_sessions(user)
    return patient


def delete_user_sessions(user):
    now = timezone.now()
    for session in Session.objects.filter(expire_date__gt=now).iterator():
        if session.get_decoded().get('_auth_user_id') == str(user.pk):
            session.delete()
