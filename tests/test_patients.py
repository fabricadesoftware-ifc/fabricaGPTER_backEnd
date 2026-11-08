from django.contrib.auth import get_user_model
from django.contrib.sessions.models import Session
from django.core.cache import cache
from django.db import IntegrityError
from django.test import TestCase, override_settings
from unittest import mock
from rest_framework.test import APIClient

from accounts.models import AccessProfile, ProfessionalProfile
from patients.models import Patient
from tests.helpers import create_patient, create_user_with_profile, make_cpf

User = get_user_model()
PASSWORD = 'Development-test-only-9482!'
ORIGIN = 'http://localhost:5173'
CSRF_SETTINGS = dict(
    SECURE_SSL_REDIRECT=False, SESSION_COOKIE_SECURE=False,
    CSRF_COOKIE_SECURE=False, ALLOWED_HOSTS=['testserver'],
    CSRF_TRUSTED_ORIGINS=[ORIGIN],
)


class PatientApiTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.professional = create_user_with_profile(
            'professional', PASSWORD, AccessProfile.Role.PROFESSIONAL,
            first_name='Profissional Teste', email='professional@example.com')
        cls.other_professional = create_user_with_profile(
            'other-professional', PASSWORD, AccessProfile.Role.PROFESSIONAL,
            first_name='Outro Profissional', email='other@example.com')
        cls.patient = create_patient(
            professional=cls.professional, username='patient', password=PASSWORD,
            name='Ana Paciente', cpf_seed='123456789',
            email='ana@example.com')
        cls.other_patient = create_patient(
            professional=cls.other_professional, username='other-patient',
            password=PASSWORD, name='Paciente Alheio', cpf_seed='987654321',
            email='alheio@example.com')

    def setUp(self):
        cache.clear()
        self.client = APIClient(enforce_csrf_checks=True)
        self.token = self.client.get('/api/auth/csrf/').json()['csrf_token']

    def login(self, username='professional', password=PASSWORD, client=None):
        client = client or self.client
        token = client.get('/api/auth/csrf/').json()['csrf_token']
        response = client.post('/api/auth/login/',
            {'username': username, 'password': password}, format='json',
            HTTP_X_CSRFTOKEN=token, HTTP_ORIGIN=ORIGIN)
        self.assertEqual(response.status_code, 200, response.content)
        self.token = response.json()['csrf_token']
        return self.token

    def assert_error(self, response, status, code):
        self.assertEqual(response.status_code, status, response.content)
        self.assertEqual(response.json()['error']['code'], code)
        self.assertEqual(set(response.json()), {'error'})

    def post_patient(self, payload, token=None):
        return self.client.post('/api/patients/', payload, format='json',
                                HTTP_X_CSRFTOKEN=token or self.token,
                                HTTP_ORIGIN=ORIGIN)


@override_settings(**CSRF_SETTINGS)
class PatientPermissionTests(PatientApiTestCase):
    def test_cors_preflight_allows_configured_origin_with_credentials(self):
        response = self.client.options(
            '/api/patients/', HTTP_ORIGIN=ORIGIN,
            HTTP_ACCESS_CONTROL_REQUEST_METHOD='POST',
            HTTP_ACCESS_CONTROL_REQUEST_HEADERS='content-type,x-csrftoken')
        self.assertEqual(response['access-control-allow-origin'], ORIGIN)
        self.assertEqual(response['access-control-allow-credentials'], 'true')
        self.assertIn('x-csrftoken', response['access-control-allow-headers'])

    def test_authentication_is_required(self):
        self.assert_error(self.client.get('/api/patients/'), 401, 'not_authenticated')
        self.assert_error(self.post_patient({}), 401, 'not_authenticated')
        self.assert_error(self.client.get('/api/profile/'), 401, 'not_authenticated')

    def test_patient_cannot_list_create_or_open_patient_records(self):
        self.login('patient')
        self.assert_error(self.client.get('/api/patients/'), 403, 'permission_denied')
        self.assert_error(self.post_patient({}), 403, 'permission_denied')
        self.assert_error(self.client.get(f'/api/patients/{self.patient.pk}/'),
                          403, 'permission_denied')
        profile = self.client.get('/api/profile/')
        self.assertEqual(profile.status_code, 200)
        self.assertEqual(profile.json()['profileId'], self.patient.pk)

    def test_professional_cannot_access_another_professionals_patient(self):
        self.login()
        self.assert_error(self.client.get(f'/api/patients/{self.other_patient.pk}/'),
                          404, 'not_found')
        listing = self.client.get('/api/patients/').json()
        self.assertEqual([item['id'] for item in listing['results']], [self.patient.pk])

    def test_profile_ids_distinguish_account_from_profile(self):
        self.login('patient')
        data = self.client.get('/api/profile/').json()
        self.assertEqual(data['id'], self.patient.user_id)
        self.assertEqual(data['profileId'], self.patient.pk)
        self.assertEqual(data['profile'], 'paciente')
        self.assertEqual(data['email'], 'ana@example.com')
        self.assertIsNone(data['phone'])
        self.assertIsNone(data['birthDate'])
        self.assertEqual(data['cpf'], self.patient.cpf)
        self.assertIsNone(data['photo'])

        professional_client = APIClient(enforce_csrf_checks=True)
        self.login('professional', client=professional_client)
        data = professional_client.get('/api/profile/').json()
        self.assertEqual(data['id'], self.professional.pk)
        self.assertEqual(data['profileId'], self.professional.access_profile.pk)
        self.assertEqual(data['profile'], 'profissional')
        self.assertIsNone(data['phone'])
        self.assertIsNone(data['cpf'])

    def test_patient_profile_returns_personal_information(self):
        self.patient.phone = '(47) 98888-2222'
        self.patient.birth_date = '1992-04-05'
        self.patient.photo = 'https://example.org/paciente.jpg'
        self.patient.save(update_fields=['phone', 'birth_date', 'photo', 'updated_at'])

        self.login('patient')
        data = self.client.get('/api/profile/').json()
        self.assertEqual(data, {
            'id': self.patient.user_id,
            'profileId': self.patient.pk,
            'profile': 'paciente',
            'username': 'patient',
            'name': 'Ana Paciente',
            'email': 'ana@example.com',
            'phone': '(47) 98888-2222',
            'birthDate': '1992-04-05',
            'cpf': self.patient.cpf,
            'photo': 'https://example.org/paciente.jpg',
        })

    def test_professional_profile_data_is_returned(self):
        ProfessionalProfile.objects.create(
            user=self.professional,
            phone='(47) 99999-1111',
            birth_date='1985-06-07',
            cpf='52998224725',
            photo='https://example.org/profissional.jpg',
        )
        self.login('professional')
        data = self.client.get('/api/profile/').json()
        self.assertEqual(data['email'], 'professional@example.com')
        self.assertEqual(data['phone'], '(47) 99999-1111')
        self.assertEqual(data['birthDate'], '1985-06-07')
        self.assertEqual(data['cpf'], '52998224725')
        self.assertEqual(data['photo'], 'https://example.org/profissional.jpg')


@override_settings(**CSRF_SETTINGS)
class PatientCreateTests(PatientApiTestCase):
    def payload(self, **overrides):
        data = {
            'username': 'novo-paciente',
            'password': 'Paciente-seguro-4821!',
            'confirmation': 'Paciente-seguro-4821!',
            'name': 'Novo Paciente',
            'email': 'novo@example.com',
            'cpf': '529.982.247-25',
            'cep': '70000-000',
            'street': 'Rua das Flores',
            'city': 'Brasília',
            'state': 'df',
            'neighborhood': 'Centro',
            'number': '42',
        }
        data.update(overrides)
        return data

    def test_create_account_and_patient_in_one_operation(self):
        self.login()
        response = self.post_patient(self.payload())
        self.assertEqual(response.status_code, 201, response.content)
        data = response.json()
        self.assertEqual(data['username'], 'novo-paciente')
        self.assertEqual(data['name'], 'Novo Paciente')
        self.assertEqual(data['cpf'], '52998224725')
        self.assertEqual(data['cep'], '70000000')
        self.assertEqual(data['state'], 'DF')
        self.assertEqual(data['status'], 'ativo')
        self.assertIsNone(data['phone'])
        self.assertIsNone(data['birthDate'])
        self.assertIsNone(data['photo'])
        self.assertEqual(data['address'], 'Rua das Flores, 42 - Centro, Brasília - DF, CEP 70000-000')
        self.assertNotIn('password', response.content.decode())
        self.assertNotIn('pbkdf2', response.content.decode())

        user = User.objects.get(username='novo-paciente')
        self.assertTrue(user.check_password('Paciente-seguro-4821!'))
        self.assertEqual(user.access_profile.role, AccessProfile.Role.PATIENT)
        patient = Patient.objects.get(pk=data['id'])
        self.assertEqual(patient.professional, self.professional)
        self.assertEqual(patient.user, user)

        patient_client = APIClient(enforce_csrf_checks=True)
        self.login('novo-paciente', 'Paciente-seguro-4821!', client=patient_client)
        me = patient_client.get('/api/auth/me/').json()['user']
        self.assertEqual(me['username'], 'novo-paciente')
        self.assertEqual(me['profile'], 'paciente')
        self.assertEqual(me['profileId'], patient.pk)

    def test_duplicate_username_cpf_and_email(self):
        self.login()
        self.assertEqual(self.post_patient(self.payload()).status_code, 201)

        cases = [
            ('username', self.payload(username='novo-paciente',
                                     email='outro@example.com', cpf=make_cpf('444444444'))),
            ('cpf', self.payload(username='outro-usuario', email='outro2@example.com')),
            ('email', self.payload(username='outro-usuario-2', cpf=make_cpf('555555555'))),
        ]
        for field, payload in cases:
            response = self.post_patient(payload)
            self.assertEqual(response.status_code, 400)
            body = response.json()['error']
            self.assertEqual(body['code'], 'validation_error')
            self.assertIn(field, body['fields'])

    def test_invalid_cpf_password_and_confirmation(self):
        self.login()
        cases = [
            ('cpf', self.payload(cpf='111.111.111-11')),
            ('password', self.payload(password='123', confirmation='123')),
            ('confirmation', self.payload(confirmation='Outra-senha-9988!')),
        ]
        for field, payload in cases:
            response = self.post_patient(payload)
            self.assertEqual(response.status_code, 400)
            self.assertEqual(response.json()['error']['code'], 'validation_error')
            self.assertIn(field, response.json()['error']['fields'])

    def test_client_cannot_choose_profile_or_owner(self):
        self.login()
        response = self.post_patient(self.payload(
            profile='profissional', professional=self.other_professional.pk,
            status='inativo', is_staff=True))
        self.assertEqual(response.status_code, 201, response.content)
        patient = Patient.objects.get(pk=response.json()['id'])
        self.assertEqual(patient.professional, self.professional)
        self.assertEqual(patient.status, Patient.Status.ACTIVE)
        self.assertEqual(patient.user.access_profile.role, AccessProfile.Role.PATIENT)
        self.assertFalse(patient.user.is_staff)

    def test_rollback_when_patient_creation_fails(self):
        self.login()
        users_before = User.objects.count()
        patients_before = Patient.objects.count()
        with mock.patch('patients.services.Patient.objects.create',
                        side_effect=IntegrityError('forced failure')):
            response = self.post_patient(self.payload())
        self.assert_error(response, 409, 'conflict')
        self.assertEqual(User.objects.count(), users_before)
        self.assertEqual(Patient.objects.count(), patients_before)
        self.assertFalse(User.objects.filter(username='novo-paciente').exists())
        self.assertFalse(AccessProfile.objects.filter(
            user__username='novo-paciente').exists())

    def test_write_requires_csrf(self):
        self.login()
        response = self.client.post('/api/patients/', self.payload(), format='json',
                                    HTTP_ORIGIN=ORIGIN)
        self.assert_error(response, 403, 'csrf_failed')


@override_settings(**CSRF_SETTINGS)
class PatientListAndDetailTests(PatientApiTestCase):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.bruno = create_patient(
            professional=cls.professional, username='bruno', password=PASSWORD,
            name='Bruno Paciente', cpf_seed='222222222', email='bruno@example.com')
        cls.carla = create_patient(
            professional=cls.professional, username='carla', password=PASSWORD,
            name='Carla Paciente', cpf_seed='333333333', email='carla@example.com')

    def test_pagination_search_and_deterministic_order(self):
        self.login()
        response = self.client.get('/api/patients/?page=1&page_size=2')
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(set(data), {'results', 'count', 'page', 'page_size'})
        self.assertEqual(data['count'], 3)
        self.assertEqual(data['page'], 1)
        self.assertEqual(data['page_size'], 2)
        self.assertEqual([item['name'] for item in data['results']],
                         ['Ana Paciente', 'Bruno Paciente'])

        page_two = self.client.get('/api/patients/?page=2&page_size=2').json()
        self.assertEqual([item['name'] for item in page_two['results']], ['Carla Paciente'])

        search = self.client.get('/api/patients/?search=bru').json()
        self.assertEqual(search['count'], 1)
        self.assertEqual(search['results'][0]['name'], 'Bruno Paciente')

        ordered = self.client.get('/api/patients/?ordering=-name').json()
        self.assertEqual([item['name'] for item in ordered['results']],
                         ['Carla Paciente', 'Bruno Paciente', 'Ana Paciente'])

    def test_detail_does_not_depend_on_listing(self):
        self.login()
        response = self.client.get(f'/api/patients/{self.bruno.pk}/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['username'], 'bruno')

    def test_invalid_query_parameters_and_not_found_are_json(self):
        self.login()
        response = self.client.get('/api/patients/?ordering=password')
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()['error']['code'], 'validation_error')
        self.assertIn('ordering', response.json()['error']['fields'])
        self.assert_error(self.client.get('/api/patients/?status=arquivado'),
                          400, 'validation_error')
        self.assert_error(self.client.get('/api/patients/999999/'), 404, 'not_found')
        self.assert_error(self.client.get('/api/patients/not-a-number/'), 404, 'not_found')

    def test_invalid_json_returns_parse_error(self):
        self.login()
        response = self.client.post('/api/patients/', '{', content_type='application/json',
                                    HTTP_X_CSRFTOKEN=self.token, HTTP_ORIGIN=ORIGIN)
        self.assert_error(response, 400, 'parse_error')


@override_settings(**CSRF_SETTINGS)
class PatientUpdateAndDeleteTests(PatientApiTestCase):
    def test_partial_update_and_empty_password_keeps_password(self):
        self.login()
        response = self.client.patch(
            f'/api/patients/{self.patient.pk}/',
            {'name': 'Ana Atualizada', 'phone': '(61) 99999-0000',
             'birthDate': '1990-02-03', 'password': '', 'confirmation': ''},
            format='json', HTTP_X_CSRFTOKEN=self.token, HTTP_ORIGIN=ORIGIN)
        self.assertEqual(response.status_code, 200, response.content)
        data = response.json()
        self.assertEqual(data['name'], 'Ana Atualizada')
        self.assertEqual(data['phone'], '(61) 99999-0000')
        self.assertEqual(data['birthDate'], '1990-02-03')
        self.patient.refresh_from_db()
        self.patient.user.refresh_from_db()
        self.assertEqual(self.patient.user.first_name, 'Ana Atualizada')
        self.assertTrue(self.patient.user.check_password(PASSWORD))

    def test_patch_rejects_password_change(self):
        self.login()
        response = self.client.patch(
            f'/api/patients/{self.patient.pk}/',
            {'password': 'Outra-senha-9988!', 'confirmation': 'Outra-senha-9988!'},
            format='json', HTTP_X_CSRFTOKEN=self.token, HTTP_ORIGIN=ORIGIN)
        self.assertEqual(response.status_code, 400)
        self.assertIn('password', response.json()['error']['fields'])
        self.patient.user.refresh_from_db()
        self.assertTrue(self.patient.user.check_password(PASSWORD))

    def test_username_update_validates_uniqueness_and_keeps_owner(self):
        self.login()
        duplicate = self.client.patch(
            f'/api/patients/{self.patient.pk}/',
            {'username': 'other-patient'}, format='json',
            HTTP_X_CSRFTOKEN=self.token, HTTP_ORIGIN=ORIGIN)
        self.assertEqual(duplicate.status_code, 400)
        self.assertIn('username', duplicate.json()['error']['fields'])

        changed = self.client.patch(
            f'/api/patients/{self.patient.pk}/',
            {'username': 'ana-nova', 'professional': self.other_professional.pk,
             'status': 'inativo', 'profile': 'profissional'},
            format='json', HTTP_X_CSRFTOKEN=self.token, HTTP_ORIGIN=ORIGIN)
        self.assertEqual(changed.status_code, 200, changed.content)
        self.assertEqual(changed.json()['username'], 'ana-nova')
        self.patient.refresh_from_db()
        self.assertEqual(self.patient.user.username, 'ana-nova')
        self.assertEqual(self.patient.professional, self.professional)
        self.assertEqual(self.patient.status, Patient.Status.ACTIVE)

    def test_delete_deactivates_account_and_revokes_sessions(self):
        patient_client = APIClient(enforce_csrf_checks=True)
        self.login('patient', client=patient_client)
        session_key = patient_client.cookies['sessionid'].value
        self.assertTrue(Session.objects.filter(session_key=session_key).exists())

        self.login()
        response = self.client.delete(
            f'/api/patients/{self.patient.pk}/',
            HTTP_X_CSRFTOKEN=self.token, HTTP_ORIGIN=ORIGIN)
        self.assertEqual(response.status_code, 204)
        self.assertEqual(response.content, b'')
        self.patient.refresh_from_db()
        self.patient.user.refresh_from_db()
        self.assertEqual(self.patient.status, Patient.Status.INACTIVE)
        self.assertFalse(self.patient.user.is_active)
        self.assertTrue(Patient.objects.filter(pk=self.patient.pk).exists())
        self.assertFalse(Session.objects.filter(session_key=session_key).exists())
        self.assert_error(patient_client.get('/api/auth/me/'), 401, 'not_authenticated')

        login_client = APIClient(enforce_csrf_checks=True)
        token = login_client.get('/api/auth/csrf/').json()['csrf_token']
        login = login_client.post('/api/auth/login/',
            {'username': 'patient', 'password': PASSWORD}, format='json',
            HTTP_X_CSRFTOKEN=token, HTTP_ORIGIN=ORIGIN)
        self.assert_error(login, 401, 'invalid_credentials')

        again = self.client.delete(
            f'/api/patients/{self.patient.pk}/',
            HTTP_X_CSRFTOKEN=self.token, HTTP_ORIGIN=ORIGIN)
        self.assertEqual(again.status_code, 204)

    def test_delete_requires_csrf(self):
        self.login()
        response = self.client.delete(f'/api/patients/{self.patient.pk}/',
                                      HTTP_ORIGIN=ORIGIN)
        self.assert_error(response, 403, 'csrf_failed')
