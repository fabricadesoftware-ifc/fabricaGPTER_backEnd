import re
from datetime import date

from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework import serializers

from .models import Patient
from .validators import normalize_cep, normalize_cpf, normalize_state

User = get_user_model()
USERNAME_RE = re.compile(r'^[\w.@+-]+$')


def patient_data(patient):
    user = patient.user
    return {
        'id': patient.pk,
        'username': user.get_username(),
        'name': patient.name,
        'email': patient.email,
        'cpf': patient.cpf,
        'cep': patient.cep,
        'street': patient.street,
        'city': patient.city,
        'state': patient.state,
        'neighborhood': patient.neighborhood,
        'number': patient.number,
        'address': patient.address,
        'status': patient.status,
        'phone': patient.phone,
        'birthDate': patient.birth_date.isoformat() if patient.birth_date else None,
        'photo': patient.photo,
    }


def _clean_text(value, *, collapse=False):
    value = str(value or '').strip()
    if collapse:
        value = ' '.join(value.split())
    return value


def _validate_username(value, *, user_id=None):
    value = _clean_text(value)
    if not value:
        raise serializers.ValidationError('Informe o usuário.')
    if len(value) > 150:
        raise serializers.ValidationError('O usuário deve ter no máximo 150 caracteres.')
    if not USERNAME_RE.match(value):
        raise serializers.ValidationError(
            'Use apenas letras, números e os caracteres @ . + - _.'
        )
    query = User.objects.filter(username__iexact=value)
    if user_id is not None:
        query = query.exclude(pk=user_id)
    if query.exists():
        raise serializers.ValidationError('Este usuário já está cadastrado.')
    return value


def _validate_email(value, *, patient=None):
    value = _clean_text(value).lower()
    if not value:
        raise serializers.ValidationError('Informe o e-mail.')
    patients = Patient.objects.filter(email__iexact=value)
    users = User.objects.filter(email__iexact=value)
    if patient is not None:
        patients = patients.exclude(pk=patient.pk)
        users = users.exclude(pk=patient.user_id)
    if patients.exists() or users.exists():
        raise serializers.ValidationError('Este e-mail já está cadastrado.')
    return value


def _validate_cpf_value(value, *, patient=None):
    try:
        cpf = normalize_cpf(value)
    except DjangoValidationError as exc:
        raise serializers.ValidationError(exc.messages) from None
    query = Patient.objects.filter(cpf=cpf)
    if patient is not None:
        query = query.exclude(pk=patient.pk)
    if query.exists():
        raise serializers.ValidationError('Este CPF já está cadastrado.')
    return cpf


def _validate_cep_value(value):
    try:
        return normalize_cep(value)
    except DjangoValidationError as exc:
        raise serializers.ValidationError(exc.messages) from None


def _validate_state_value(value):
    try:
        return normalize_state(value)
    except DjangoValidationError as exc:
        raise serializers.ValidationError(exc.messages) from None


def _validate_password_value(value, attrs, confirmation):
    if not value:
        raise serializers.ValidationError({'password': ['Informe a senha.']})
    if value != confirmation:
        raise serializers.ValidationError(
            {'confirmation': ['A confirmação não confere com a senha.']})
    user = User(username=attrs.get('username', ''), email=attrs.get('email', ''),
                first_name=attrs.get('name', ''))
    try:
        validate_password(value, user=user)
    except DjangoValidationError as exc:
        raise serializers.ValidationError({'password': list(exc.messages)}) from None
    return value


class PatientCreateSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=150)
    password = serializers.CharField(max_length=4096, trim_whitespace=False, write_only=True)
    confirmation = serializers.CharField(max_length=4096, trim_whitespace=False, write_only=True)
    name = serializers.CharField(max_length=150)
    email = serializers.EmailField(max_length=254)
    cpf = serializers.CharField(max_length=14)
    cep = serializers.CharField(max_length=9)
    street = serializers.CharField(max_length=255)
    city = serializers.CharField(max_length=255)
    state = serializers.CharField(max_length=2)
    neighborhood = serializers.CharField(max_length=255)
    number = serializers.CharField(max_length=20)
    phone = serializers.CharField(max_length=20, required=False, allow_blank=True, allow_null=True)
    birthDate = serializers.DateField(required=False, allow_null=True,
                                      input_formats=['%Y-%m-%d'])
    photo = serializers.CharField(max_length=500, required=False, allow_blank=True, allow_null=True)

    def validate_username(self, value):
        return _validate_username(value)

    def validate_email(self, value):
        return _validate_email(value)

    def validate_cpf(self, value):
        return _validate_cpf_value(value)

    def validate_cep(self, value):
        return _validate_cep_value(value)

    def validate_state(self, value):
        return _validate_state_value(value)

    def validate_birthDate(self, value):
        if value and value > date.today():
            raise serializers.ValidationError('A data de nascimento não pode ser futura.')
        return value

    def validate(self, attrs):
        attrs['name'] = _clean_text(attrs['name'], collapse=True)
        attrs['street'] = _clean_text(attrs['street'], collapse=True)
        attrs['city'] = _clean_text(attrs['city'], collapse=True)
        attrs['neighborhood'] = _clean_text(attrs['neighborhood'], collapse=True)
        attrs['number'] = _clean_text(attrs['number'])
        if not attrs['name']:
            raise serializers.ValidationError({'name': ['Informe o nome.']})
        for field in ('street', 'city', 'neighborhood', 'number'):
            if not attrs[field]:
                raise serializers.ValidationError({field: ['Este campo é obrigatório.']})
        attrs['phone'] = _clean_text(attrs.get('phone')) or None
        attrs['photo'] = _clean_text(attrs.get('photo')) or None
        password = attrs.get('password')
        _validate_password_value(password, attrs, attrs.get('confirmation'))
        return attrs


class PatientUpdateSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=150, required=False)
    password = serializers.CharField(max_length=4096, trim_whitespace=False, write_only=True,
                                     required=False, allow_blank=True, allow_null=True)
    confirmation = serializers.CharField(max_length=4096, trim_whitespace=False, write_only=True,
                                         required=False, allow_blank=True, allow_null=True)
    name = serializers.CharField(max_length=150, required=False)
    email = serializers.EmailField(max_length=254, required=False)
    cpf = serializers.CharField(max_length=14, required=False)
    cep = serializers.CharField(max_length=9, required=False)
    street = serializers.CharField(max_length=255, required=False)
    city = serializers.CharField(max_length=255, required=False)
    state = serializers.CharField(max_length=2, required=False)
    neighborhood = serializers.CharField(max_length=255, required=False)
    number = serializers.CharField(max_length=20, required=False)
    phone = serializers.CharField(max_length=20, required=False, allow_blank=True, allow_null=True)
    birthDate = serializers.DateField(required=False, allow_null=True,
                                      input_formats=['%Y-%m-%d'])
    photo = serializers.CharField(max_length=500, required=False, allow_blank=True, allow_null=True)

    @property
    def patient(self):
        return self.context['patient']

    def validate_username(self, value):
        return _validate_username(value, user_id=self.patient.user_id)

    def validate_email(self, value):
        return _validate_email(value, patient=self.patient)

    def validate_cpf(self, value):
        return _validate_cpf_value(value, patient=self.patient)

    def validate_cep(self, value):
        return _validate_cep_value(value)

    def validate_state(self, value):
        return _validate_state_value(value)

    def validate_birthDate(self, value):
        if value and value > date.today():
            raise serializers.ValidationError('A data de nascimento não pode ser futura.')
        return value

    def validate(self, attrs):
        errors = {}
        if attrs.get('password') or attrs.get('confirmation'):
            errors['password'] = ['A senha não pode ser alterada por este endpoint.']
        if 'name' in attrs:
            attrs['name'] = _clean_text(attrs['name'], collapse=True)
            if not attrs['name']:
                errors['name'] = ['Informe o nome.']
        for field in ('street', 'city', 'neighborhood', 'number'):
            if field in attrs:
                attrs[field] = _clean_text(attrs[field], collapse=field != 'number')
                if not attrs[field]:
                    errors[field] = ['Este campo é obrigatório.']
        if 'phone' in attrs:
            attrs['phone'] = _clean_text(attrs['phone']) or None
        if 'photo' in attrs:
            attrs['photo'] = _clean_text(attrs['photo']) or None
        if errors:
            raise serializers.ValidationError(errors)
        attrs.pop('password', None)
        attrs.pop('confirmation', None)
        return attrs
