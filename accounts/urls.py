from django.urls import path
from .views import CSRFView, LoginView, LogoutView, MeView

app_name = 'accounts'
urlpatterns = [
    path('csrf/', CSRFView.as_view(), name='csrf'),
    path('login/', LoginView.as_view(), name='login'),
    path('me/', MeView.as_view(), name='me'),
    path('logout/', LogoutView.as_view(), name='logout'),
]
