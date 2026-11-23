from rest_framework.authentication import SessionAuthentication as DRFSessionAuthentication
from rest_framework.exceptions import PermissionDenied


class CSRFError(PermissionDenied):
    default_detail = 'Token CSRF ausente ou inválido.'
    default_code = 'csrf_failed'


class SessionAuthentication(DRFSessionAuthentication):
    def authenticate_header(self, request):
        return 'Session'

    def enforce_csrf(self, request):
        try:
            super().enforce_csrf(request)
        except PermissionDenied:
            raise CSRFError() from None
