import re

from django.contrib.auth import get_user_model

from accounts.models import AccessProfile
from patients.models import Patient

User = get_user_model()


def make_cpf(seed):
    """Build a CPF with valid check digits from 9 arbitrary digits."""
    base = re.sub(r'\D', '', str(seed))[:9].ljust(9, '0')
    digits = [int(item) for item in base]
    for size in (9, 10):
        total = sum(digit * weight for digit, weight in
                    zip(digits[:size], range(size + 1, 1, -1)))
        check = (total * 10) % 11
        digits.append(0 if check == 10 else check)
    return ''.join(str(item) for item in digits)


def create_user_with_profile(username, password, role, **extra):
    user = User.objects.create_user(username=username, password=password, **extra)
    AccessProfile.objects.create(user=user, role=role)
    return user


def create_patient(*, professional, username, password, name, cpf_seed, email=None,
                   status=Patient.Status.ACTIVE, **extra):
    cpf = make_cpf(cpf_seed)
    user = create_user_with_profile(
        username, password, AccessProfile.Role.PATIENT,
        first_name=name, email=email or f'{username}@example.com')
    return Patient.objects.create(
        user=user,
        professional=professional,
        name=name,
        email=email or f'{username}@example.com',
        cpf=cpf,
        cep=extra.pop('cep', '70000000'),
        street=extra.pop('street', 'Rua Exemplo'),
        city=extra.pop('city', 'Brasília'),
        state=extra.pop('state', 'DF'),
        neighborhood=extra.pop('neighborhood', 'Centro'),
        number=extra.pop('number', '100'),
        phone=extra.pop('phone', None),
        birth_date=extra.pop('birth_date', None),
        photo=extra.pop('photo', None),
        status=status,
        **extra,
    )
