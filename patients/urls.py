from django.urls import path

from .views import (AssessmentDetailView, AssessmentListView, PatientDetailView,
                    PatientListView, ProfileView, PublicPatientRegistrationView)

app_name = 'patients'
urlpatterns = [
    path('assessments/', AssessmentListView.as_view(), name='assessments'),
    path('assessments/<int:pk>/', AssessmentDetailView.as_view(), name='assessment'),
    path('patients/', PatientListView.as_view(), name='patient-list'),
    path('patients/register/', PublicPatientRegistrationView.as_view(), name='public-registration'),
    path('patients/<int:pk>/', PatientDetailView.as_view(), name='patient-detail'),
    path('patients/<int:patient_id>/assessments/', AssessmentListView.as_view(),
         name='assessment-list'),
    path('patients/<int:patient_id>/assessments/<int:pk>/', AssessmentDetailView.as_view(),
         name='assessment-detail'),
    path('profile/', ProfileView.as_view(), name='profile'),
]
