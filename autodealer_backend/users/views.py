from django.core.mail import send_mail
from django.db import transaction
from django.template.loader import render_to_string
from django.utils.crypto import get_random_string
from django_filters.rest_framework import DjangoFilterBackend
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import filters, mixins, permissions, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet, ViewSet
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from ..config import settings
from .filters import CustomerFilter
from .models import Customer, User
from .serializers import (
    CustomerSerializer,
    EmailVerificationSerializer,
    PasswordResetConfirmSerializer,
    PasswordResetRequestSerializer,
    UserRegistrationSerializer,
    UserSerializer,
)


class AuthViewSet(ViewSet):
    permission_classes = [permissions.AllowAny]

    def _send_verification_email(self, user):
        subject = "Verify your email"
        verification_url = f"http://ваш-api-домен/api/auth/verify-email/?token={user.verification_token}"
        html_message = render_to_string(
            "email_verification.html",
            {
                "user": user,
                "verification_url": verification_url,
                "token": user.verification_token,
            },
        )
        send_mail(
            subject,
            html_message,
            settings.DEFAULT_FROM_EMAIL,
            [user.email],
            html_message=html_message,
            fail_silently=False,
        )

    def _send_password_reset_email(self, user):
        subject = "Password Reset Request"
        message = render_to_string(
            "password_reset_email.html",
            {
                "user": user,
                "reset_url": f"{settings.FRONTEND_URL}/reset-password/{user.verification_token}/",
            },
        )
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [user.email],
            html_message=message,
            fail_silently=False,
        )

    @swagger_auto_schema(
        request_body=UserRegistrationSerializer,
        responses={
            201: openapi.Response("User registered", UserSerializer),
            400: "Invalid data",
            500: "Internal server error",
        },
    )
    @transaction.atomic
    @action(detail=False, methods=["post"], url_path="register")
    def register(self, request):
        serializer = UserRegistrationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            with transaction.atomic():
                user = serializer.save()
                Customer.objects.create(user=user)
                self._send_verification_email(user)

                return Response(
                    {
                        "detail": "User registered successfully. Please check your email for verification."
                    },
                    status=status.HTTP_201_CREATED,
                )

        except Exception as e:
            return Response(
                {"detail": f"Registration failed: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    @swagger_auto_schema(
        request_body=EmailVerificationSerializer,
        responses={
            200: "Email successfully verified",
            400: "Invalid token or email already verified",
        },
    )
    @action(detail=False, methods=["post"], url_path="verify-email")
    def verify_email(self, request):
        serializer = EmailVerificationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        token = serializer.validated_data["token"]
        try:
            user = User.objects.get(verification_token=token)
            if not user.is_verified:
                user.is_verified = True
                user.verification_token = None
                user.save()
                return Response(
                    {"detail": "Email successfully verified."},
                    status=status.HTTP_200_OK,
                )
            return Response(
                {"detail": "Email already verified."}, status=status.HTTP_200_OK
            )
        except User.DoesNotExist:
            return Response(
                {"detail": "Invalid verification token."},
                status=status.HTTP_400_BAD_REQUEST,
            )

    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=["email", "password"],
            properties={
                "email": openapi.Schema(type=openapi.TYPE_STRING, format="email"),
                "password": openapi.Schema(type=openapi.TYPE_STRING, format="password"),
            },
        ),
        responses={
            200: openapi.Response(
                description="Login successful",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "refresh": openapi.Schema(type=openapi.TYPE_STRING),
                        "access": openapi.Schema(type=openapi.TYPE_STRING),
                    },
                ),
            ),
            401: "Invalid credentials",
        },
    )
    @action(detail=False, methods=["post"], url_path="login")
    def login(self, request):
        return TokenObtainPairView.as_view()(request._request)

    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=["refresh"],
            properties={"refresh": openapi.Schema(type=openapi.TYPE_STRING)},
        ),
        responses={205: "Successfully logged out", 400: "Invalid token"},
    )
    @action(detail=False, methods=["post"], url_path="logout")
    def logout(self, request):
        refresh_token = request.data.get("refresh")
        if not refresh_token:
            return Response(
                {"detail": "refresh token is required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response(
                {"detail": "Successfully logged out"},
                status=status.HTTP_205_RESET_CONTENT,
            )
        except Exception as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(
        request_body=PasswordResetRequestSerializer,
        responses={
            200: "Password reset link has been sent to your email",
            400: "User with this email does not exist",
        },
    )
    @action(detail=False, methods=["post"], url_path="password-reset")
    def password_reset(self, request):
        serializer = PasswordResetRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data["email"]
        try:
            user = User.objects.get(email=email)
            if not user.verification_token:
                user.verification_token = get_random_string(64)
                user.save()
            self._send_password_reset_email(user)
            return Response(
                {"detail": "Password reset link has been sent to your email."},
                status=status.HTTP_200_OK,
            )
        except User.DoesNotExist:
            return Response(
                {"detail": "User with this email does not exist."},
                status=status.HTTP_400_BAD_REQUEST,
            )

    @swagger_auto_schema(
        request_body=PasswordResetConfirmSerializer,
        responses={
            200: "Password has been reset successfully",
            400: "Invalid reset token or passwords mismatch",
        },
    )
    @action(detail=False, methods=["post"], url_path="password-reset-confirm")
    def password_reset_confirm(self, request):
        serializer = PasswordResetConfirmSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        token = serializer.validated_data["token"]
        new_password = serializer.validated_data["new_password"]

        try:
            user = User.objects.get(verification_token=token)
            user.set_password(new_password)
            user.verification_token = None
            user.save()
            return Response(
                {"detail": "Password has been reset successfully."},
                status=status.HTTP_200_OK,
            )
        except User.DoesNotExist:
            return Response(
                {"detail": "Invalid reset token."}, status=status.HTTP_400_BAD_REQUEST
            )

    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=["refresh"],
            properties={"refresh": openapi.Schema(type=openapi.TYPE_STRING)},
        ),
        responses={
            200: openapi.Response(
                description="Token refreshed",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={"access": openapi.Schema(type=openapi.TYPE_STRING)},
                ),
            ),
            401: "Invalid token",
        },
    )
    @action(detail=False, methods=["post"], url_path="refresh")
    def refresh(self, request):
        return TokenRefreshView.as_view()(request._request)


# User = get_user_model()
# class UserViewSet(mixins.CreateModelMixin,
#                   mixins.RetrieveModelMixin,
#                   mixins.UpdateModelMixin,
#                   mixins.ListModelMixin,
#                   GenericViewSet):
#     queryset = User.objects.all()
#     serializer_class = UserSerializer
#     filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
#     filterset_class = UserFilter
#     search_fields = ['email', 'username']
#     ordering_fields = ['date_joined']
#     permission_classes = [permissions.IsAuthenticatedOrReadOnly]
#
#     def get_permissions(self):
#         if self.action == 'create':
#             return [permissions.AllowAny()]
#         elif self.action == 'list':
#             return [IsAdminUser()]
#         return [IsAuthenticated()]
#
#     @swagger_auto_schema(
#         manual_parameters=[
#             openapi.Parameter('email', openapi.IN_QUERY, type=openapi.TYPE_STRING,
#                               description='Поиск по email (регистронезависимый)'),
#             openapi.Parameter('is_verified', openapi.IN_QUERY, type=openapi.TYPE_BOOLEAN,
#                               description='Фильтр по верификации'),
#             openapi.Parameter('created_at_after', openapi.IN_QUERY, type=openapi.TYPE_STRING,
#                               format='date', description='Дата регистрации после (YYYY-MM-DD)'),
#             openapi.Parameter('ordering', openapi.IN_QUERY, type=openapi.TYPE_STRING,
#                               description='Сортировка: date_joined, -date_joined')
#         ]
#     )
#     def list(self, request, *args, **kwargs):
#         return super().list(request, *args, **kwargs)
#
#     @action(detail=False, methods=['get'])
#     def me(self, request):
#         serializer = self.get_serializer(request.user)
#         return Response(serializer.data)


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
