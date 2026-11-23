from django.test import TestCase, override_settings
from rest_framework.test import APIClient


@override_settings(GPTER_SUPPORT_EMAIL='', GPTER_SUPPORT_PHONE='',
                   GPTER_TERMS_UPDATED_AT='', GPTER_TERMS_VERSION='',
                   GPTER_TERMS_SECTIONS=[])
class EmptyContentTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_support_empty_state(self):
        response = self.client.get('/api/support/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {'email': None, 'phone': None})

    def test_terms_empty_state(self):
        response = self.client.get('/api/terms/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {
            'updatedAt': None, 'version': None, 'sections': []})


@override_settings(
    GPTER_SUPPORT_EMAIL='suporte@example.org',
    GPTER_SUPPORT_PHONE='(00) 0000-0000',
    GPTER_TERMS_UPDATED_AT='2026-01-15',
    GPTER_TERMS_VERSION='1.0',
    GPTER_TERMS_SECTIONS=[
        {'id': 'uso', 'title': 'Uso do serviço', 'content': 'Conteúdo configurado.'},
        {'id': 'privacidade', 'title': 'Privacidade', 'content': 'Outro conteúdo.'},
    ],
)
class ConfiguredContentTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_support_configuration(self):
        self.assertEqual(self.client.get('/api/support/').json(), {
            'email': 'suporte@example.org', 'phone': '(00) 0000-0000'})

    def test_terms_preserve_section_order(self):
        data = self.client.get('/api/terms/').json()
        self.assertEqual(data['updatedAt'], '2026-01-15')
        self.assertEqual(data['version'], '1.0')
        self.assertEqual([item['id'] for item in data['sections']],
                         ['uso', 'privacidade'])
        self.assertEqual(data['sections'][0]['title'], 'Uso do serviço')
