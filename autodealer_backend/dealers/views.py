from django_filters.rest_framework import DjangoFilterBackend
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import viewsets, filters, mixins, permissions
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import GenericViewSet

from .filters import DealerFilter
from .models import Dealer
from .serializers import DealerSerializer


class DealerViewSet(mixins.ListModelMixin,
                    mixins.RetrieveModelMixin,
                    mixins.UpdateModelMixin,
                    GenericViewSet):
    queryset = Dealer.objects.all()
    serializer_class = DealerSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = DealerFilter
    search_fields = ['name']
    ordering_fields = ['balance', 'created_at']

    def get_permissions(self):
        if self.action == 'list':
            return [IsAuthenticated()]
        return [IsAuthenticated(), permissions.DjangoModelPermissions()]

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter(
                name='search',
                in_=openapi.IN_QUERY,
                type=openapi.TYPE_STRING,
                description='Поиск по названию дилера'
            ),
            openapi.Parameter(
                name='location',
                in_=openapi.IN_QUERY,
                type=openapi.TYPE_STRING,
                description='Код страны (например, US, RU)'
            ),
            openapi.Parameter(
                name='balance__gt',
                in_=openapi.IN_QUERY,
                type=openapi.TYPE_NUMBER,
                description='Минимальный баланс'
            ),
            openapi.Parameter(
                name='balance__lt',
                in_=openapi.IN_QUERY,
                type=openapi.TYPE_NUMBER,
                description='Максимальный баланс'
            ),
            openapi.Parameter(
                name='is_active',
                in_=openapi.IN_QUERY,
                type=openapi.TYPE_BOOLEAN,
                description='Только активные дилеры'
            ),
            openapi.Parameter(
                name='ordering',
                in_=openapi.IN_QUERY,
                type=openapi.TYPE_STRING,
                description='Сортировка: balance, -balance, created_at, -created_at'
            )
        ]
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)
