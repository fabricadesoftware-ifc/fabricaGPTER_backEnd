from django.db import IntegrityError
from django.shortcuts import get_object_or_404
from django.utils.decorators import method_decorator
from django.views.decorators.debug import sensitive_post_parameters
from rest_framework import status
from rest_framework.exceptions import PermissionDenied
from rest_framework.parsers import JSONParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from accounts.errors import ConflictError, FieldValidationError
from accounts.models import AccessProfile, ProfessionalProfile

from .models import Patient
from .pagination import PatientPagination
from .permissions import IsProfessional
from .serializers import (PatientCreateSerializer, PatientUpdateSerializer,
                          patient_data)
from .services import create_patient_account, deactivate_patient, update_patient

ORDERING_FIELDS = {'name', 'status', 'created_at', 'updated_at'}


@method_decorator(sensitive_post_parameters('password', 'confirmation'), name='dispatch')
class PatientListView(APIView):
    permission_classes = [IsAuthenticated, IsProfessional]
    parser_classes = [JSONParser]
    pagination_class = PatientPagination

    def get_queryset(self):
        queryset = Patient.objects.select_related('user').filter(
            professional=self.request.user)
        search = self.request.query_params.get('search', '').strip()
        if search:
            queryset = queryset.filter(name__icontains=search)
        patient_status = self.request.query_params.get('status', '').strip()
        if patient_status:
            if patient_status not in Patient.Status.values:
                raise FieldValidationError({
                    'status': [f'Use um destes valores: {", ".join(Patient.Status.values)}.']
                })
            queryset = queryset.filter(status=patient_status)

        ordering = self.request.query_params.get('ordering', 'name').strip()
        descending = ordering.startswith('-')
        field = ordering.lstrip('-')
        if field not in ORDERING_FIELDS:
            raise FieldValidationError({
                'ordering': ['Use um destes valores: ' + ', '.join(
                    sorted(ORDERING_FIELDS | {'-' + item for item in ORDERING_FIELDS})
                ) + '.']
            })
        order = ('-' if descending else '') + field
        return queryset.order_by(order, 'id')

    def get(self, request):
        paginator = self.pagination_class()
        page = paginator.paginate_queryset(self.get_queryset(), request, view=self)
        return paginator.get_paginated_response([patient_data(item) for item in page])

    def post(self, request):
        serializer = PatientCreateSerializer(data=request.data)
        if not serializer.is_valid():
            raise FieldValidationError(serializer.errors)
        try:
            patient = create_patient_account(
                professional=request.user, data=serializer.validated_data)
        except IntegrityError:
            raise ConflictError(
                'Não foi possível concluir o cadastro porque um dado já está em uso.'
            ) from None
        return Response(patient_data(patient), status=status.HTTP_201_CREATED)


@method_decorator(sensitive_post_parameters('password', 'confirmation'), name='dispatch')
class PatientDetailView(APIView):
    permission_classes = [IsAuthenticated, IsProfessional]
    parser_classes = [JSONParser]

    def get_object(self):
        return get_object_or_404(
            Patient.objects.select_related('user'),
            pk=self.kwargs['pk'],
            professional=self.request.user,
        )

    def get(self, request, pk):
        return Response(patient_data(self.get_object()))

    def patch(self, request, pk):
        patient = self.get_object()
        serializer = PatientUpdateSerializer(
            data=request.data, partial=True, context={'patient': patient})
        if not serializer.is_valid():
            raise FieldValidationError(serializer.errors)
        try:
            patient = update_patient(patient, serializer.validated_data)
        except IntegrityError:
            raise ConflictError(
                'Não foi possível salvar porque um dado já está em uso.'
            ) from None
        return Response(patient_data(patient))

    def delete(self, request, pk):
        deactivate_patient(self.get_object())
        return Response(status=status.HTTP_204_NO_CONTENT)


class ProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        try:
            access_profile = user.access_profile
        except AccessProfile.DoesNotExist:
            raise PermissionDenied('Perfil de acesso não configurado.') from None

        if access_profile.role == AccessProfile.Role.PATIENT:
            patient = getattr(user, 'patient', None)
            if patient is not None:
                data = patient_data(patient)
                return Response({
                    'id': user.pk,
                    'profileId': patient.pk,
                    'profile': access_profile.role,
                    'username': data['username'],
                    'name': data['name'],
                    'email': data['email'],
                    'phone': data['phone'],
                    'birthDate': data['birthDate'],
                    'cpf': data['cpf'],
                    'photo': data['photo'],
                })
            return Response({
                'id': user.pk,
                'profileId': None,
                'profile': access_profile.role,
                'username': user.get_username(),
                'name': user.get_full_name().strip() or user.get_username(),
                'email': user.email or None,
                'phone': None,
                'birthDate': None,
                'cpf': None,
                'photo': None,
            })

        try:
            professional_profile = user.professional_profile
        except ProfessionalProfile.DoesNotExist:
            professional_profile = None

        return Response({
            'id': user.pk,
            'profileId': access_profile.pk,
            'profile': access_profile.role,
            'username': user.get_username(),
            'name': user.get_full_name().strip() or user.get_username(),
            'email': user.email or None,
            'phone': professional_profile.phone if professional_profile else None,
            'birthDate': (
                professional_profile.birth_date.isoformat()
                if professional_profile and professional_profile.birth_date else None
            ),
            'cpf': professional_profile.cpf if professional_profile else None,
            'photo': professional_profile.photo if professional_profile else None,
        })
