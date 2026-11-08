from django.http import Http404, JsonResponse
from rest_framework.exceptions import APIException
from rest_framework.views import exception_handler as drf_exception_handler


class FieldValidationError(APIException):
    status_code = 400
    default_detail = 'Revise os campos informados.'
    default_code = 'validation_error'

    def __init__(self, fields=None, detail=None, code=None):
        self.fields = fields or {}
        super().__init__(detail=detail, code=code)


class ConflictError(APIException):
    status_code = 409
    default_detail = 'O recurso conflita com dados existentes.'
    default_code = 'conflict'

    def __init__(self, detail=None, fields=None):
        self.fields = fields or {}
        super().__init__(detail=detail)


def csrf_failure(request, reason=''):
    response = JsonResponse({'error': {'code': 'csrf_failed',
                                      'message': 'Token CSRF ausente ou inválido.'}}, status=403)
    response['Cache-Control'] = 'no-store'
    return response


def not_found(request, exception=None):
    response = JsonResponse({'error': {
        'code': 'not_found', 'message': 'Recurso não encontrado.'}}, status=404)
    response['Cache-Control'] = 'no-store'
    return response


def server_error(request):
    response = JsonResponse({'error': {
        'code': 'server_error', 'message': 'Erro interno do servidor.'}}, status=500)
    response['Cache-Control'] = 'no-store'
    return response


def exception_handler(exc, context):
    response = drf_exception_handler(exc, context)
    if response is None:
        return None
    code = 'not_found' if isinstance(exc, Http404) else getattr(
        exc, 'default_code', 'request_error')
    messages = {
        'not_authenticated': 'Autenticação necessária ou sessão expirada.',
        'authentication_failed': 'Autenticação necessária ou sessão expirada.',
        'invalid_credentials': 'Usuário ou senha inválidos.',
        'permission_denied': 'Acesso não autorizado.',
        'csrf_failed': 'Token CSRF ausente ou inválido.',
        'invalid': 'Dados de entrada inválidos.',
        'validation_error': 'Revise os campos informados.',
        'parse_error': 'JSON inválido.',
        'throttled': 'Muitas tentativas. Tente novamente mais tarde.',
        'method_not_allowed': 'Método não permitido.',
        'unsupported_media_type': 'Use Content-Type: application/json.',
        'not_found': 'Recurso não encontrado.',
        'conflict': 'O recurso conflita com dados existentes.',
    }
    error = {'code': code, 'message': messages.get(code, 'Requisição inválida.')}
    fields = getattr(exc, 'fields', None)
    if fields:
        error['fields'] = fields
    response.data = {'error': error}
    response['Cache-Control'] = 'no-store'
    return response
