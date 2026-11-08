from django.conf import settings
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView


class SupportView(APIView):
    authentication_classes = []
    permission_classes = [AllowAny]

    def get(self, request):
        return Response({
            'email': settings.GPTER_SUPPORT_EMAIL or None,
            'phone': settings.GPTER_SUPPORT_PHONE or None,
        })


class TermsView(APIView):
    authentication_classes = []
    permission_classes = [AllowAny]

    def get(self, request):
        return Response({
            'updatedAt': settings.GPTER_TERMS_UPDATED_AT or None,
            'version': settings.GPTER_TERMS_VERSION or None,
            'sections': settings.GPTER_TERMS_SECTIONS,
        })
