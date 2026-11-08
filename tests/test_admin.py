from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from accounts.models import AccessProfile, ProfessionalProfile
from patients.models import Patient


class ProfessionalAdminTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.admin = get_user_model().objects.create_superuser(
            username='admin', password='Admin-password-123!', email='admin@example.com')
        cls.professional = get_user_model().objects.create_user(
            username='professional', password='Professional-password-123!',
            first_name='Profissional', email='professional@example.com')
        AccessProfile.objects.create(user=cls.professional, role='profissional')
        cls.patient = get_user_model().objects.create_user(
            username='patient', password='Patient-password-123!',
            email='patient@example.com', first_name='Paciente')
        AccessProfile.objects.create(user=cls.patient, role='paciente')
        Patient.objects.create(
            user=cls.patient,
            professional=cls.professional,
            name='Paciente',
            email='patient@example.com',
            cpf='52998224725',
            cep='70000000',
            street='Rua A',
            city='Brasília',
            state='DF',
            neighborhood='Centro',
            number='10',
        )

    def setUp(self):
        self.client.force_login(self.admin)

    def test_professional_user_admin_has_editable_profile_fields(self):
        response = self.client.get(
            reverse('admin:auth_user_change', args=[self.professional.pk]))
        self.assertEqual(response.status_code, 200)
        for field in ('phone', 'birth_date', 'cpf', 'photo'):
            self.assertContains(response, f'name="professional_profile-0-{field}"')

        response = self.client.post(
            reverse('admin:auth_user_change', args=[self.professional.pk]),
            {
                'username': 'professional',
                'first_name': 'Profissional Atualizado',
                'last_name': '',
                'email': 'professional@example.com',
                'is_active': 'on',
                'is_staff': '',
                'is_superuser': '',
                'groups': [],
                'user_permissions': [],
                'date_joined_0': '2026-01-01',
                'date_joined_1': '00:00:00',
                'last_login_0': '',
                'last_login_1': '',
                'password': self.professional.password,
                'professional_profile-TOTAL_FORMS': '1',
                'professional_profile-INITIAL_FORMS': '0',
                'professional_profile-MIN_NUM_FORMS': '0',
                'professional_profile-MAX_NUM_FORMS': '1',
                'professional_profile-0-phone': '(47) 99999-1111',
                'professional_profile-0-birth_date': '07/06/1985',
                'professional_profile-0-cpf': '52998224725',
                'professional_profile-0-photo': 'https://example.org/profissional.jpg',
                'professional_profile-0-id': '',
                'professional_profile-0-user': str(self.professional.pk),
                '_save': 'Salvar',
            },
        )
        self.assertEqual(response.status_code, 302)
        profile = ProfessionalProfile.objects.get(user=self.professional)
        self.assertEqual(profile.phone, '(47) 99999-1111')
        self.assertEqual(profile.birth_date.isoformat(), '1985-06-07')
        self.assertEqual(profile.cpf, '52998224725')
        self.assertEqual(profile.photo, 'https://example.org/profissional.jpg')

    def test_patient_user_admin_does_not_show_professional_inline(self):
        response = self.client.get(reverse('admin:auth_user_change', args=[self.patient.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, 'Informações do profissional')

    def test_patient_user_admin_has_editable_profile_fields(self):
        response = self.client.get(reverse('admin:auth_user_change', args=[self.patient.pk]))
        self.assertEqual(response.status_code, 200)
        for field in ('phone', 'birth_date', 'cpf', 'photo'):
            self.assertContains(response, f'name="patient-0-{field}"')
        self.assertContains(response, 'Informações do paciente')

        response = self.client.post(
            reverse('admin:auth_user_change', args=[self.patient.pk]),
            {
                'username': 'patient',
                'first_name': 'Paciente',
                'last_name': '',
                'email': 'patient@example.com',
                'is_active': 'on',
                'is_staff': '',
                'is_superuser': '',
                'groups': [],
                'user_permissions': [],
                'date_joined_0': '2026-01-01',
                'date_joined_1': '00:00:00',
                'last_login_0': '',
                'last_login_1': '',
                'password': self.patient.password,
                'patient-TOTAL_FORMS': '1',
                'patient-INITIAL_FORMS': '1',
                'patient-MIN_NUM_FORMS': '0',
                'patient-MAX_NUM_FORMS': '1',
                'patient-0-id': str(self.patient.patient.pk),
                'patient-0-user': str(self.patient.pk),
                'patient-0-phone': '(47) 98888-2222',
                'patient-0-birth_date': '05/04/1992',
                'patient-0-cpf': '52998224725',
                'patient-0-photo': 'https://example.org/paciente.jpg',
                '_save': 'Salvar',
            },
        )
        self.assertEqual(response.status_code, 302)
        profile = Patient.objects.get(user=self.patient)
        self.assertEqual(profile.phone, '(47) 98888-2222')
        self.assertEqual(profile.birth_date.isoformat(), '1992-04-05')
        self.assertEqual(profile.cpf, '52998224725')
        self.assertEqual(profile.photo, 'https://example.org/paciente.jpg')
