from django.http import JsonResponse
from rest_framework.views import exception_handler as drf_exception_handler


def csrf_failure(request, reason=''):
    response = JsonResponse({'error': {'code': 'csrf_failed',
                                      'message': 'Token CSRF ausente ou inválido.'}}, status=403)
    response['Cache-Control'] = 'no-store'
    return response


def exception_handler(exc, context):
    response = drf_exception_handler(exc, context)
    if response is None:
        return None
    code = getattr(exc, 'default_code', 'request_error')
    messages = {
        'not_authenticated': 'Autenticação necessária ou sessão expirada.',
        'authentication_failed': 'Autenticação necessária ou sessão expirada.',
        'invalid_credentials': 'Usuário ou senha inválidos.',
        'permission_denied': 'Acesso não autorizado.',
        'csrf_failed': 'Token CSRF ausente ou inválido.',
        'invalid': 'Dados de entrada inválidos.',
        'parse_error': 'JSON inválido.',
        'throttled': 'Muitas tentativas. Tente novamente mais tarde.',
        'method_not_allowed': 'Método não permitido.',
        'unsupported_media_type': 'Use Content-Type: application/json.',
    }
    response.data = {'error': {'code': code, 'message': messages.get(code, 'Requisição inválida.')}}
    response['Cache-Control'] = 'no-store'
    return response
