from django.conf import settings
from django.test import SimpleTestCase, override_settings
from django.urls import reverse

class HealthCheckTests(SimpleTestCase):
    def test_health_check(self):
        response = self.client.get(reverse('health-check'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {'status': 'ok'})

    def test_health_check_rejects_post(self):
        self.assertEqual(self.client.post(reverse('health-check')).status_code, 405)

    @override_settings(CORS_ALLOWED_ORIGINS=['http://localhost:5173'])
    def test_cors_allows_only_configured_origin(self):
        allowed = self.client.get(reverse('health-check'), HTTP_ORIGIN='http://localhost:5173')
        denied = self.client.get(reverse('health-check'), HTTP_ORIGIN='http://example.com')
        self.assertEqual(allowed['access-control-allow-origin'], 'http://localhost:5173')
        self.assertNotIn('access-control-allow-origin', denied)

    def test_essential_settings(self):
        self.assertIsInstance(settings.DEBUG, bool)
        self.assertTrue(settings.SECRET_KEY)
        self.assertFalse(getattr(settings, 'CORS_ALLOW_ALL_ORIGINS', False))
