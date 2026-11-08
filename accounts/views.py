from datetime import timedelta

from django.conf import settings
from django.contrib.auth import (authenticate, login, logout,
                                 update_session_auth_hash)
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError as DjangoValidationError
from django.middleware.csrf import get_token, rotate_token
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

from .errors import FieldValidationError
from .models import AccessProfile


def user_data(user):
    try:
        access_profile = user.access_profile
    except AccessProfile.DoesNotExist:
        access_profile = None
    role = access_profile.role if access_profile else None
    profile_id = None
    if role == AccessProfile.Role.PATIENT:
        patient = getattr(user, 'patient', None)
        profile_id = patient.pk if patient is not None else None
    elif role == AccessProfile.Role.PROFESSIONAL:
        profile_id = access_profile.pk
    return {
        'id': user.pk,
        'username': user.get_username(),
        'display_name': user.get_full_name().strip() or user.get_username(),
        'profile': role,
        'profileId': profile_id,
    }


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


class ChangePasswordInput(serializers.Serializer):
    current_password = serializers.CharField(max_length=4096, trim_whitespace=False,
                                             write_only=True)
    new_password = serializers.CharField(max_length=4096, trim_whitespace=False,
                                         write_only=True)
    confirmation = serializers.CharField(max_length=4096, trim_whitespace=False,
                                         write_only=True)

    def validate_current_password(self, value):
        if not self.context['user'].check_password(value):
            raise serializers.ValidationError('A senha atual está incorreta.')
        return value

    def validate(self, attrs):
        if attrs['new_password'] != attrs['confirmation']:
            raise serializers.ValidationError(
                {'confirmation': ['A confirmação não confere com a nova senha.']})
        if attrs['new_password'] == attrs['current_password']:
            raise serializers.ValidationError(
                {'new_password': ['A nova senha deve ser diferente da senha atual.']})
        try:
            validate_password(attrs['new_password'], user=self.context['user'])
        except DjangoValidationError as exc:
            raise serializers.ValidationError(
                {'new_password': list(exc.messages)}) from None
        return attrs


@method_decorator(never_cache, name='dispatch')
@method_decorator(sensitive_post_parameters(
    'current_password', 'new_password', 'confirmation'), name='dispatch')
class ChangePasswordView(AuthView):
    def post(self, request):
        serializer = ChangePasswordInput(data=request.data, context={'user': request.user})
        if not serializer.is_valid():
            raise FieldValidationError(serializer.errors)
        user = request.user
        user.set_password(serializer.validated_data['new_password'])
        user.save(update_fields=['password'])
        # Keep this session valid; every other session is invalidated by the
        # password hash stored in Django's session authentication data.
        update_session_auth_hash(request, user)
        rotate_token(request)
        return Response({
            'detail': 'Senha alterada com sucesso.',
            'csrf_token': get_token(request),
        })
