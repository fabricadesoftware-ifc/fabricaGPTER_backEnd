from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.test import TestCase, override_settings
from rest_framework.test import APIClient

from accounts.models import AccessProfile
from tests.helpers import create_user_with_profile

User = get_user_model()
OLD_PASSWORD = 'Development-test-only-9482!'
NEW_PASSWORD = 'Nova-senha-segura-7755!'
ORIGIN = 'http://localhost:5173'


@override_settings(SECURE_SSL_REDIRECT=False, SESSION_COOKIE_SECURE=False,
                   CSRF_COOKIE_SECURE=False, ALLOWED_HOSTS=['testserver'],
                   CSRF_TRUSTED_ORIGINS=[ORIGIN])
class ChangePasswordTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = create_user_with_profile(
            'professional', OLD_PASSWORD, AccessProfile.Role.PROFESSIONAL)

    def setUp(self):
        cache.clear()
        self.client = APIClient(enforce_csrf_checks=True)
        self.token = self.login(self.client)
        self.other_client = APIClient(enforce_csrf_checks=True)
        self.login(self.other_client)

    def login(self, client):
        token = client.get('/api/auth/csrf/').json()['csrf_token']
        response = client.post('/api/auth/login/',
            {'username': 'professional', 'password': OLD_PASSWORD}, format='json',
            HTTP_X_CSRFTOKEN=token, HTTP_ORIGIN=ORIGIN)
        self.assertEqual(response.status_code, 200, response.content)
        return response.json()['csrf_token']

    def change(self, payload, token=None):
        return self.client.post('/api/auth/change-password/', payload, format='json',
                                HTTP_X_CSRFTOKEN=token or self.token,
                                HTTP_ORIGIN=ORIGIN)

    def test_requires_authentication_and_csrf(self):
        anonymous = APIClient(enforce_csrf_checks=True)
        token = anonymous.get('/api/auth/csrf/').json()['csrf_token']
        response = anonymous.post('/api/auth/change-password/', {
            'current_password': OLD_PASSWORD,
            'new_password': NEW_PASSWORD,
            'confirmation': NEW_PASSWORD,
        }, format='json', HTTP_X_CSRFTOKEN=token, HTTP_ORIGIN=ORIGIN)
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.json()['error']['code'], 'not_authenticated')

        response = self.client.post('/api/auth/change-password/', {
            'current_password': OLD_PASSWORD,
            'new_password': NEW_PASSWORD,
            'confirmation': NEW_PASSWORD,
        }, format='json', HTTP_ORIGIN=ORIGIN)
        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.json()['error']['code'], 'csrf_failed')

    def test_validates_current_password_confirmation_and_policy(self):
        response = self.change({
            'current_password': 'senha-errada',
            'new_password': NEW_PASSWORD,
            'confirmation': NEW_PASSWORD,
        })
        self.assertEqual(response.status_code, 400)
        self.assertIn('current_password', response.json()['error']['fields'])

        response = self.change({
            'current_password': OLD_PASSWORD,
            'new_password': NEW_PASSWORD,
            'confirmation': 'Outra-confirmacao-9911!',
        })
        self.assertEqual(response.status_code, 400)
        self.assertIn('confirmation', response.json()['error']['fields'])

        response = self.change({
            'current_password': OLD_PASSWORD,
            'new_password': '123',
            'confirmation': '123',
        })
        self.assertEqual(response.status_code, 400)
        self.assertIn('new_password', response.json()['error']['fields'])

        response = self.change({
            'current_password': OLD_PASSWORD,
            'new_password': OLD_PASSWORD,
            'confirmation': OLD_PASSWORD,
        })
        self.assertEqual(response.status_code, 400)
        self.assertIn('new_password', response.json()['error']['fields'])

    def test_changes_password_keeps_current_session_and_revokes_others(self):
        old_token = self.token
        response = self.change({
            'current_password': OLD_PASSWORD,
            'new_password': NEW_PASSWORD,
            'confirmation': NEW_PASSWORD,
        })
        self.assertEqual(response.status_code, 200, response.content)
        body = response.json()
        self.assertEqual(body['detail'], 'Senha alterada com sucesso.')
        self.assertTrue(body['csrf_token'])
        self.assertNotEqual(body['csrf_token'], old_token)

        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password(NEW_PASSWORD))
        self.assertEqual(self.client.get('/api/auth/me/').status_code, 200)
        other_me = self.other_client.get('/api/auth/me/')
        self.assertEqual(other_me.status_code, 401)
        self.assertEqual(other_me.json()['error']['code'], 'not_authenticated')

        login_client = APIClient(enforce_csrf_checks=True)
        token = login_client.get('/api/auth/csrf/').json()['csrf_token']
        old_login = login_client.post('/api/auth/login/',
            {'username': 'professional', 'password': OLD_PASSWORD}, format='json',
            HTTP_X_CSRFTOKEN=token, HTTP_ORIGIN=ORIGIN)
        self.assertEqual(old_login.status_code, 401)
        token = login_client.get('/api/auth/csrf/').json()['csrf_token']
        new_login = login_client.post('/api/auth/login/',
            {'username': 'professional', 'password': NEW_PASSWORD}, format='json',
            HTTP_X_CSRFTOKEN=token, HTTP_ORIGIN=ORIGIN)
        self.assertEqual(new_login.status_code, 200, new_login.content)

        stale = self.client.post('/api/auth/logout/', {},
                                 format='json', HTTP_X_CSRFTOKEN=old_token,
                                 HTTP_ORIGIN=ORIGIN)
        self.assertEqual(stale.status_code, 403)
        self.assertEqual(stale.json()['error']['code'], 'csrf_failed')
        logout = self.client.post('/api/auth/logout/', {}, format='json',
                                  HTTP_X_CSRFTOKEN=body['csrf_token'], HTTP_ORIGIN=ORIGIN)
        self.assertEqual(logout.status_code, 204)
        self.assertEqual(self.client.get('/api/auth/me/').status_code, 401)
