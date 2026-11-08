"""Configuração inicial do projeto Fábrica GPTER."""
import os
from pathlib import Path

from django.core.exceptions import ImproperlyConfigured
import dj_database_url
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / '.env')

def env_list(name, default=''):
    return [item.strip() for item in os.getenv(name, default).split(',') if item.strip()]

SECRET_KEY = os.getenv('SECRET_KEY', '')
if not SECRET_KEY:
    raise ImproperlyConfigured('Defina SECRET_KEY no ambiente ou no arquivo .env.')
debug_value = os.getenv('DJANGO_DEBUG', 'false').strip().lower()
if debug_value not in ('true', 'false'):
    raise ImproperlyConfigured('DJANGO_DEBUG deve ser true ou false.')
DEBUG = debug_value == 'true'
ALLOWED_HOSTS = env_list(
    'ALLOWED_HOSTS',
    'localhost,127.0.0.1,gpter-server.class.fabricadesoftware.ifc.edu.br',
)
CORS_ALLOWED_ORIGINS = env_list(
    'CORS_ALLOWED_ORIGINS',
    'http://localhost:5173,https://gpter.class.fabricadesoftware.ifc.edu.br',
)
INSTALLED_APPS = [
    'django.contrib.admin', 'django.contrib.auth', 'django.contrib.contenttypes',
    'django.contrib.sessions', 'django.contrib.messages', 'django.contrib.staticfiles',
    'corsheaders', 'rest_framework', 'accounts', 'patients',
]
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware', 'whitenoise.middleware.WhiteNoiseMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware', 'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware', 'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware', 'django.middleware.clickjacking.XFrameOptionsMiddleware',
]
ROOT_URLCONF = 'config.urls'
TEMPLATES = [{
    'BACKEND': 'django.template.backends.django.DjangoTemplates', 'DIRS': [], 'APP_DIRS': True,
    'OPTIONS': {'context_processors': [
        'django.template.context_processors.request', 'django.contrib.auth.context_processors.auth',
        'django.contrib.messages.context_processors.messages',
    ]},
}]
WSGI_APPLICATION = 'config.wsgi.application'
ASGI_APPLICATION = 'config.asgi.application'
DATABASES = {
    'default': dj_database_url.config(
        default=f"sqlite:///{os.getenv('SQLITE_PATH', str(BASE_DIR / 'local.sqlite3'))}",
        conn_max_age=600,
    )
}
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]
LANGUAGE_CODE = 'pt-br'
TIME_ZONE = 'America/Sao_Paulo'
USE_I18N = True
USE_TZ = True
STATIC_URL = 'static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

def env_bool(name, default):
    value = os.getenv(name, str(default)).strip().lower()
    if value not in ('true', 'false'):
        raise ImproperlyConfigured(f'{name} deve ser true ou false.')
    return value == 'true'

CORS_ALLOW_CREDENTIALS = True
CORS_EXPOSE_HEADERS = ['Retry-After', 'WWW-Authenticate']
CSRF_TRUSTED_ORIGINS = env_list(
    'CSRF_TRUSTED_ORIGINS',
    'http://localhost:5173,https://gpter.class.fabricadesoftware.ifc.edu.br',
)
SESSION_ENGINE = 'django.contrib.sessions.backends.db'
SESSION_COOKIE_HTTPONLY = True
CSRF_COOKIE_HTTPONLY = True
SESSION_COOKIE_SECURE = env_bool('SESSION_COOKIE_SECURE', not DEBUG)
CSRF_COOKIE_SECURE = env_bool('CSRF_COOKIE_SECURE', not DEBUG)
SESSION_COOKIE_SAMESITE = os.getenv('SESSION_COOKIE_SAMESITE', 'Lax')
CSRF_COOKIE_SAMESITE = os.getenv('CSRF_COOKIE_SAMESITE', 'Lax')
for cookie_name in ('SESSION', 'CSRF'):
    same_site = globals()[f'{cookie_name}_COOKIE_SAMESITE']
    if same_site not in ('Lax', 'Strict', 'None'):
        raise ImproperlyConfigured(f'{cookie_name}_COOKIE_SAMESITE inválido.')
    if same_site == 'None' and not globals()[f'{cookie_name}_COOKIE_SECURE']:
        raise ImproperlyConfigured('SameSite=None exige cookie Secure.')
SESSION_COOKIE_AGE = int(os.getenv('SESSION_COOKIE_AGE', '28800'))
if SESSION_COOKIE_AGE <= 0:
    raise ImproperlyConfigured('SESSION_COOKIE_AGE deve ser positivo.')
SESSION_SAVE_EVERY_REQUEST = False
CSRF_FAILURE_VIEW = 'accounts.errors.csrf_failure'
SECURE_SSL_REDIRECT = env_bool('SECURE_SSL_REDIRECT', not DEBUG)
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
SECURE_HSTS_SECONDS = int(os.getenv('SECURE_HSTS_SECONDS', '0'))
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': ['accounts.authentication.SessionAuthentication'],
    'DEFAULT_PERMISSION_CLASSES': ['rest_framework.permissions.IsAuthenticated'],
    'DEFAULT_RENDERER_CLASSES': ['rest_framework.renderers.JSONRenderer'],
    'EXCEPTION_HANDLER': 'accounts.errors.exception_handler',
    'DEFAULT_THROTTLE_RATES': {'login': os.getenv('LOGIN_THROTTLE_RATE', '10/min')},
}
