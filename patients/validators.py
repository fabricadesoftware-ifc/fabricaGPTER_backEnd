import re

from django.core.exceptions import ValidationError

BRAZILIAN_STATES = {
    'AC', 'AL', 'AP', 'AM', 'BA', 'CE', 'DF', 'ES', 'GO', 'MA', 'MT', 'MS',
    'MG', 'PA', 'PB', 'PR', 'PE', 'PI', 'RJ', 'RN', 'RS', 'RO', 'RR', 'SC',
    'SP', 'SE', 'TO',
}


def digits_only(value):
    return re.sub(r'\D', '', str(value or ''))


def normalize_cpf(value):
    cpf = digits_only(value)
    if len(cpf) != 11:
        raise ValidationError('Informe um CPF com 11 dígitos.')
    if cpf == cpf[0] * 11:
        raise ValidationError('Informe um CPF válido.')
    for size in (9, 10):
        total = sum(int(digit) * weight for digit, weight in
                    zip(cpf[:size], range(size + 1, 1, -1)))
        check = (total * 10) % 11
        if check == 10:
            check = 0
        if check != int(cpf[size]):
            raise ValidationError('Informe um CPF válido.')
    return cpf


def normalize_cep(value):
    cep = digits_only(value)
    if len(cep) != 8:
        raise ValidationError('Informe um CEP com 8 dígitos.')
    return cep


def normalize_state(value):
    state = str(value or '').strip().upper()
    if state not in BRAZILIAN_STATES:
        raise ValidationError('Informe uma UF válida.')
    return state
