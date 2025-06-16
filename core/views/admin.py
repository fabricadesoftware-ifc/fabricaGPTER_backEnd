from django.shortcuts import render
from rest_framework.viewsets import ModelViewSet

from core.models.admin import Admin
from core.serializers.admin import AdminSerializer


class AdminViewSet(ModelViewSet):
    queryset = Admin.objects.all()
    serializer_class = AdminSerializer