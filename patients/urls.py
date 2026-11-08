from django.urls import path

from .views import PatientDetailView, PatientListView, ProfileView

app_name = 'patients'
urlpatterns = [
    path('patients/', PatientListView.as_view(), name='patient-list'),
    path('patients/<int:pk>/', PatientDetailView.as_view(), name='patient-detail'),
    path('profile/', ProfileView.as_view(), name='profile'),
]
