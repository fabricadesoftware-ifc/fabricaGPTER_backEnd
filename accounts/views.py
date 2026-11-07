from datetime import timedelta
from django.conf import settings
from django.contrib.auth import authenticate, login, logout
from django.middleware.csrf import get_token
from django.utils.decorators import method_decorator
from django.utils import timezone
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.cache import never_cache
from django.views.decorators.debug import sensitive_post_parameters
from rest_framework import serializers
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.parsers import JSONParser
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.throttling import SimpleRateThrottle
from rest_framework.views import APIView
from .models import AccessProfile


def user_data(user):
    try:
        role = user.access_profile.role
    except AccessProfile.DoesNotExist:
        role = None
    return {'id': user.pk, 'username': user.get_username(),
            'display_name': user.get_full_name().strip() or user.get_username(), 'profile': role}


class InvalidCredentials(AuthenticationFailed):
    default_code = 'invalid_credentials'


class LoginThrottle(SimpleRateThrottle):
    scope = 'login'

    def get_cache_key(self, request, view):
        # Forwarded headers are client-controlled unless a trusted proxy sanitizes
        # them. Use the connection address; clients behind a proxy share its limit.
        ident = request.META.get('REMOTE_ADDR') or 'unknown'
        return self.cache_format % {'scope': self.scope, 'ident': ident}


class LoginInput(serializers.Serializer):
    username = serializers.CharField(max_length=150, trim_whitespace=False)
    password = serializers.CharField(max_length=4096, trim_whitespace=False, write_only=True)


@method_decorator(never_cache, name='dispatch')
class AuthView(APIView):
    parser_classes = [JSONParser]


class CSRFView(AuthView):
    authentication_classes = []
    permission_classes = [AllowAny]

    def get(self, request):
        return Response({'csrf_token': get_token(request)})


@method_decorator(csrf_protect, name='dispatch')
@method_decorator(sensitive_post_parameters('password'), name='dispatch')
class LoginView(AuthView):
    authentication_classes = []
    permission_classes = [AllowAny]
    throttle_classes = [LoginThrottle]

    def post(self, request):
        data = LoginInput(data=request.data)
        data.is_valid(raise_exception=True)
        user = authenticate(request=request, **data.validated_data)
        if user is None:
            raise InvalidCredentials()
        login(request, user)
        # Absolute lifetime: reading /me does not renew the session.
        request.session.set_expiry(timezone.now() + timedelta(seconds=settings.SESSION_COOKIE_AGE))
        return Response({'user': user_data(user), 'csrf_token': get_token(request)})

    def get_authenticate_header(self, request):
        return 'Session'


class MeView(AuthView):
    def get(self, request):
        return Response({'user': user_data(request.user)})


class LogoutView(AuthView):
    def post(self, request):
        logout(request)
        return Response(status=204)
