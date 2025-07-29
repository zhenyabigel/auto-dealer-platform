from django.contrib.auth import get_user_model
from django_filters.rest_framework import DjangoFilterBackend
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import filters, mixins, permissions, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from .filters import CustomerFilter, UserFilter
from .models import Customer
from .serializers import CustomerSerializer, UserSerializer

User = get_user_model()


class UserViewSet(
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    mixins.ListModelMixin,
    GenericViewSet,
):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]
    filterset_class = UserFilter
    search_fields = ["email", "username"]
    ordering_fields = ["date_joined"]
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_permissions(self):
        if self.action == "create":
            return [permissions.AllowAny()]
        elif self.action == "list":
            return [IsAdminUser()]
        return [IsAuthenticated()]

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter(
                "email",
                openapi.IN_QUERY,
                type=openapi.TYPE_STRING,
                description="Поиск по email (регистронезависимый)",
            ),
            openapi.Parameter(
                "is_verified",
                openapi.IN_QUERY,
                type=openapi.TYPE_BOOLEAN,
                description="Фильтр по верификации",
            ),
            openapi.Parameter(
                "created_at_after",
                openapi.IN_QUERY,
                type=openapi.TYPE_STRING,
                format="date",
                description="Дата регистрации после (YYYY-MM-DD)",
            ),
            openapi.Parameter(
                "ordering",
                openapi.IN_QUERY,
                type=openapi.TYPE_STRING,
                description="Сортировка: date_joined, -date_joined",
            ),
        ]
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @action(detail=False, methods=["get"])
    def me(self, request):
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)


class CustomerViewSet(
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    mixins.ListModelMixin,
    GenericViewSet,
):
    queryset = Customer.objects.select_related("user").all()
    serializer_class = CustomerSerializer
    permission_classes = [IsAdminUser]
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]
    filterset_class = CustomerFilter
    search_fields = ["user__email", "address"]
    ordering_fields = ["balance", "created_at"]

    def get_permissions(self):
        if self.action == "list":
            return [IsAdminUser()]
        return [IsAuthenticated()]

    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=["email", "username", "password", "password2"],
            properties={
                "email": openapi.Schema(type=openapi.TYPE_STRING, format="email"),
                "username": openapi.Schema(type=openapi.TYPE_STRING),
                "password": openapi.Schema(type=openapi.TYPE_STRING, format="password"),
                "password2": openapi.Schema(
                    type=openapi.TYPE_STRING, format="password"
                ),
                "phone": openapi.Schema(type=openapi.TYPE_STRING),
                "is_verified": openapi.Schema(type=openapi.TYPE_BOOLEAN),
            },
        ),
        responses={201: UserSerializer, 400: "Неверные данные"},
    )
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    @action(detail=False, methods=["get"], permission_classes=[IsAuthenticated])
    def me(self, request):
        customer = request.user.customer
        serializer = self.get_serializer(customer)
        return Response(serializer.data)
