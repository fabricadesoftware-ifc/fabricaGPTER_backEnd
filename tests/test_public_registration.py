from unittest.mock import patch

from django.db import IntegrityError
from django.test import override_settings
from django.urls import reverse

from patients.models import Patient
from patients.views import RegistrationThrottle
from tests.helpers import make_cpf
from tests.test_patients import CSRF_SETTINGS, PatientApiTestCase, User


@override_settings(**CSRF_SETTINGS)
class PublicRegistrationTests(PatientApiTestCase):
    url = reverse('patients:public-registration')

    def setUp(self):
        super().setUp()
        self.payload = {
            'name': 'Maria Silva', 'cpf': make_cpf('345678912'),
            'email': 'Maria@example.com', 'dominantHand': 'Direita',
            'cep': '88000-000', 'street': 'Rua das Flores', 'number': '12',
            'neighborhood': 'Centro', 'city': 'Florianópolis', 'state': 'sc',
        }

    def register(self, **changes):
        return self.client.post(self.url, self.payload | changes, format='json')

    def test_form_to_professional_consultation(self):
        page = self.client.get(reverse('patient-registration-form'))
        self.assertContains(page, f'action="{self.url}"')
        accounts = User.objects.count()
        response = self.register(professional=self.professional.pk, username='ignored')
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.content, b'')
        patient = Patient.objects.get(cpf=self.payload['cpf'])
        self.assertIsNone(patient.user_id)
        self.assertIsNone(patient.professional_id)
        self.assertEqual(User.objects.count(), accounts)
        self.assertEqual(patient.email, 'maria@example.com')
        self.assertEqual(patient.cep, '88000000')
        detail = reverse('patients:patient-detail', args=[patient.pk])
        self.assertEqual(self.client.get(detail).status_code, 401)
        self.client.force_authenticate(self.patient.user)
        self.assertEqual(self.client.get(detail).status_code, 403)
        for professional in (self.professional, self.other_professional):
            self.client.force_authenticate(professional)
            result = self.client.get('/api/patients/', {'search': 'Maria'}).json()['results']
            self.assertEqual([row['id'] for row in result], [patient.pk])
            self.assertEqual(self.client.get(detail).json(), result[0])
            self.assertIsNone(result[0]['username'])
            self.assertEqual(self.client.patch(detail, {}, format='json').status_code, 404)
            self.assertEqual(self.client.delete(detail).status_code, 404)

    def test_invalid_required_fields_and_duplicates(self):
        invalid = self.client.post(self.url, {'cpf': '11'}, format='json')
        self.assert_error(invalid, 400, 'validation_error')
        self.assertIn('name', invalid.json()['error']['fields'])
        self.assertIn('cpf', invalid.json()['error']['fields'])
        initial = Patient.objects.count()
        self.assertEqual(self.register().status_code, 201)
        for changes in ({'cpf': make_cpf('678912345'), 'email': 'MARIA@example.com'},
                        {'email': 'outra@example.com'}, {'cpf': self.patient.cpf}):
            response = self.register(**changes)
            self.assert_error(response, 409, 'conflict')
            self.assertNotIn('fields', response.json()['error'])
        self.assertEqual(Patient.objects.count(), initial + 1)

    @patch('patients.views.create_patient_record', side_effect=IntegrityError)
    def test_concurrent_conflict(self, create):
        self.assert_error(self.register(), 409, 'conflict')
        create.assert_called_once()

    @patch.object(RegistrationThrottle, 'get_rate', return_value='1/min')
    def test_throttle_includes_invalid_attempts(self, get_rate):
        self.assertEqual(self.register(cpf='1').status_code, 400)
        response = self.client.post(self.url, self.payload, format='json',
                                    HTTP_X_FORWARDED_FOR='192.0.2.20')
        self.assert_error(response, 429, 'throttled')
        self.assertIn('Retry-After', response)
