from datetime import timedelta
from django.contrib.auth import get_user_model
from django.contrib.sessions.models import Session
from django.core.cache import cache
from django.db import IntegrityError, transaction
from django.test import TestCase, override_settings
from django.utils import timezone
from rest_framework.test import APIClient, APIRequestFactory, force_authenticate
from rest_framework.permissions import IsAdminUser
from rest_framework.views import APIView
from rest_framework.response import Response
from accounts.models import AccessProfile


@override_settings(SECURE_SSL_REDIRECT=False, SESSION_COOKIE_SECURE=False,
                   CSRF_COOKIE_SECURE=False, ALLOWED_HOSTS=['testserver'],
                   CSRF_TRUSTED_ORIGINS=['http://localhost:5173'])
class AuthenticationTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.password = 'Development-test-only-9482!'
        cls.patient = get_user_model().objects.create_user(username='patient', password=cls.password, first_name='Ana')
        cls.professional = get_user_model().objects.create_user(username='professional', password=cls.password)
        cls.unassigned = get_user_model().objects.create_user(username='unassigned', password=cls.password, is_staff=True)
        AccessProfile.objects.create(user=cls.patient, role='paciente')
        AccessProfile.objects.create(user=cls.professional, role='profissional')

    def setUp(self):
        cache.clear()
        self.client = APIClient(enforce_csrf_checks=True)
        self.token = self.client.get('/api/auth/csrf/').json()['csrf_token']

    def login(self, username='patient', password=None):
        return self.client.post('/api/auth/login/',
            {'username': username, 'password': password or self.password}, format='json',
            HTTP_X_CSRFTOKEN=self.token, HTTP_ORIGIN='http://localhost:5173')

    def assert_error(self, response, status, code):
        self.assertEqual(response.status_code, status)
        self.assertEqual(response.json()['error']['code'], code)
        self.assertEqual(set(response.json()), {'error'})

    def test_login_and_me_for_both_profiles(self):
        for username, role, name in [('patient', 'paciente', 'Ana'), ('professional', 'profissional', 'professional')]:
            response = self.login(username)
            self.assertEqual(response.status_code, 200)
            expected = {'id': get_user_model().objects.get(username=username).pk,
                        'username': username, 'display_name': name, 'profile': role}
            self.assertEqual(response.json()['user'], expected)
            self.assertEqual(self.client.get('/api/auth/me/').json(), {'user': expected})
            self.assertTrue(response.cookies['sessionid']['httponly'])
            self.assertEqual(response.cookies['sessionid']['samesite'], 'Lax')
            self.assertIn('no-store', response['Cache-Control'])
            self.token = response.json()['csrf_token']

    def test_missing_profile_does_not_infer_role(self):
        self.assertIsNone(self.login('unassigned').json()['user']['profile'])

    def test_invalid_unknown_and_inactive_credentials(self):
        invalid = self.login(password='wrong')
        unknown = self.login('unknown')
        self.patient.is_active = False
        self.patient.save()
        inactive = self.login()
        for response in (invalid, unknown, inactive):
            self.assert_error(response, 401, 'invalid_credentials')
            self.assertEqual(response.json(), invalid.json())
        self.assertNotIn('sessionid', self.client.cookies)

    def test_missing_authentication(self):
        self.assert_error(self.client.get('/api/auth/me/'), 401, 'not_authenticated')
        self.assert_error(self.client.post('/api/auth/logout/'), 401, 'not_authenticated')

    def test_login_csrf_and_origin(self):
        data = {'username': 'patient', 'password': self.password}
        self.assert_error(self.client.post('/api/auth/login/', data, format='json'), 403, 'csrf_failed')
        self.assert_error(self.client.post('/api/auth/login/', data, format='json',
            HTTP_X_CSRFTOKEN=self.token, HTTP_ORIGIN='https://evil.example'), 403, 'csrf_failed')

    def test_logout_csrf_and_revocation(self):
        response = self.login()
        key = self.client.cookies['sessionid'].value
        self.assert_error(self.client.post('/api/auth/logout/'), 403, 'csrf_failed')
        self.assert_error(self.client.post('/api/auth/logout/', HTTP_X_CSRFTOKEN=self.token), 403, 'csrf_failed')
        response = self.client.post('/api/auth/logout/', HTTP_X_CSRFTOKEN=response.json()['csrf_token'])
        self.assertEqual(response.status_code, 204)
        self.assertEqual(response.content, b'')
        self.assertFalse(Session.objects.filter(session_key=key).exists())
        self.client.cookies['sessionid'] = key
        self.assert_error(self.client.get('/api/auth/me/'), 401, 'not_authenticated')

    def test_expired_session(self):
        self.login()
        Session.objects.filter(session_key=self.client.cookies['sessionid'].value).update(
            expire_date=timezone.now() - timedelta(seconds=1))
        self.assert_error(self.client.get('/api/auth/me/'), 401, 'not_authenticated')

    def test_me_does_not_extend_session(self):
        self.login()
        session = Session.objects.get(session_key=self.client.cookies['sessionid'].value)
        self.client.get('/api/auth/me/')
        self.assertEqual(Session.objects.get(pk=session.pk).expire_date, session.expire_date)

    def test_login_switching_user_invalidates_old_session(self):
        self.login()
        key = self.client.cookies['sessionid'].value
        self.token = self.client.get('/api/auth/csrf/').json()['csrf_token']
        self.login('professional')
        self.assertNotEqual(self.client.cookies['sessionid'].value, key)
        self.assertFalse(Session.objects.filter(session_key=key).exists())

    def test_malformed_input(self):
        for data in ({}, {'username': 'patient'}, {'username': 'patient', 'password': ''}):
            self.assert_error(self.client.post('/api/auth/login/', data, format='json',
                HTTP_X_CSRFTOKEN=self.token), 400, 'invalid')
        self.assert_error(self.client.post('/api/auth/login/', '{', content_type='application/json',
            HTTP_X_CSRFTOKEN=self.token), 400, 'parse_error')

    def test_login_rate_limit(self):
        for _ in range(10):
            self.login(password='wrong')
        response = self.login(password='wrong')
        self.assert_error(response, 429, 'throttled')
        self.assertIn('Retry-After', response)

    def test_login_rate_limit_ignores_spoofed_forwarded_headers(self):
        def attempt(remote_addr, forwarded_addr):
            return self.client.post('/api/auth/login/',
                {'username': 'patient', 'password': 'wrong'}, format='json',
                HTTP_X_CSRFTOKEN=self.token, REMOTE_ADDR=remote_addr,
                HTTP_X_FORWARDED_FOR=forwarded_addr,
                HTTP_X_REAL_IP=forwarded_addr,
                HTTP_FORWARDED=f'for={forwarded_addr}')

        for index in range(10):
            self.assert_error(attempt('192.0.2.1', f'198.51.100.{index + 1}'),
                              401, 'invalid_credentials')
        response = attempt('192.0.2.1', '198.51.100.11')
        self.assert_error(response, 429, 'throttled')
        self.assertIn('Retry-After', response)
        # A different connection IP still has its own allowance.
        self.assert_error(attempt('192.0.2.2', '198.51.100.11'),
                          401, 'invalid_credentials')

    def test_cors_preflight(self):
        for origin, allowed in [('http://localhost:5173', True), ('https://evil.example', False)]:
            response = self.client.options('/api/auth/login/', HTTP_ORIGIN=origin,
                HTTP_ACCESS_CONTROL_REQUEST_METHOD='POST',
                HTTP_ACCESS_CONTROL_REQUEST_HEADERS='content-type,x-csrftoken')
            self.assertEqual('access-control-allow-origin' in response, allowed)
            if allowed:
                self.assertEqual(response['access-control-allow-credentials'], 'true')
                self.assertIn('x-csrftoken', response['access-control-allow-headers'])

    @override_settings(SESSION_COOKIE_SECURE=True, CSRF_COOKIE_SECURE=True)
    def test_secure_cookie_flags(self):
        response = self.login()
        for cookie in ('sessionid', 'csrftoken'):
            self.assertTrue(response.cookies[cookie]['secure'])
            self.assertTrue(response.cookies[cookie]['httponly'])

    def test_profile_database_constraint(self):
        with self.assertRaises(IntegrityError), transaction.atomic():
            AccessProfile.objects.create(user=self.unassigned, role='invalid')

    def test_password_change_invalidates_session(self):
        self.login()
        self.patient.set_password('Another-development-password-49!')
        self.patient.save()
        self.assert_error(self.client.get('/api/auth/me/'), 401, 'not_authenticated')

    def test_get_cannot_login_or_logout(self):
        self.assert_error(self.client.get('/api/auth/login/'), 405, 'method_not_allowed')
        self.login()
        self.assert_error(self.client.get('/api/auth/logout/'), 405, 'method_not_allowed')

    def test_default_protection_and_permission_error(self):
        class ProtectedView(APIView):
            def get(self, request):
                return Response({'ok': True})

        request = APIRequestFactory().get('/')
        response = ProtectedView.as_view()(request)
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.data['error']['code'], 'not_authenticated')
        force_authenticate(request, user=self.patient)
        response = ProtectedView.as_view(permission_classes=[IsAdminUser])(request)
        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.data, {'error': {
            'code': 'permission_denied', 'message': 'Acesso não autorizado.'}})
