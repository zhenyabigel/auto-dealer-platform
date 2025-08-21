from django.core.mail import send_mail
from django.template.loader import render_to_string
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from autodealer_backend.config import settings
from autodealer_backend.users.models import User
from autodealer_backend.users.serializers import (
    CustomTokenObtainPairSerializer,
    EmailVerificationSerializer,
    PasswordResetConfirmSerializer,
    PasswordResetRequestSerializer,
    UserRegistrationSerializer,
)


class AuthViewSet(GenericViewSet):
    permission_classes = [permissions.AllowAny]

    @swagger_auto_schema(
        operation_description="Регистрация нового пользователя",
        request_body=UserRegistrationSerializer,
        responses={
            201: openapi.Response(
                description="Успешная регистрация",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "detail": openapi.Schema(
                            type=openapi.TYPE_STRING, description="Сообщение об успехе"
                        )
                    },
                ),
            ),
            400: "Неверные данные",
        },
    )
    @action(detail=False, methods=["post"], permission_classes=[permissions.AllowAny])
    def register(self, request):
        serializer = UserRegistrationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        self._send_verification_email(user)

        return Response(
            {"detail": "User registered successfully. Please check your email."},
            status=status.HTTP_201_CREATED,
        )

    @swagger_auto_schema(
        operation_description="Аутентификация пользователя",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=["email", "password"],
            properties={
                "email": openapi.Schema(
                    type=openapi.TYPE_STRING,
                    format="email",
                    description="Email пользователя",
                ),
                "password": openapi.Schema(
                    type=openapi.TYPE_STRING,
                    format="password",
                    description="Пароль пользователя",
                ),
            },
        ),
        responses={
            200: openapi.Response(
                description="Успешная аутентификация",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "refresh": openapi.Schema(
                            type=openapi.TYPE_STRING, description="Refresh токен"
                        ),
                        "access": openapi.Schema(
                            type=openapi.TYPE_STRING, description="Access токен"
                        ),
                    },
                ),
            ),
            401: "Неверные учетные данные",
        },
    )
    @action(detail=False, methods=["post"], permission_classes=[permissions.AllowAny])
    def login(self, request):
        return TokenObtainPairView.as_view()(
            request._request, serializer_class=CustomTokenObtainPairSerializer
        )

    @swagger_auto_schema(
        operation_description="Обновление access токена",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=["refresh"],
            properties={
                "refresh": openapi.Schema(
                    type=openapi.TYPE_STRING, description="Refresh токен"
                ),
            },
        ),
        responses={
            200: openapi.Response(
                description="Токен обновлен",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "access": openapi.Schema(
                            type=openapi.TYPE_STRING, description="Новый access токен"
                        ),
                    },
                ),
            ),
            401: "Неверный refresh токен",
        },
    )
    @action(detail=False, methods=["post"], permission_classes=[permissions.AllowAny])
    def refresh(self, request):
        return TokenRefreshView.as_view()(request._request)

    @swagger_auto_schema(
        operation_description="Подтверждение email адреса",
        request_body=EmailVerificationSerializer,
        responses={
            200: openapi.Response(
                description="Email подтвержден",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "detail": openapi.Schema(
                            type=openapi.TYPE_STRING, description="Сообщение об успехе"
                        )
                    },
                ),
            ),
            400: "Неверный или просроченный токен",
        },
    )
    @action(detail=False, methods=["post"], permission_classes=[permissions.AllowAny])
    def verify_email(self, request):
        serializer = EmailVerificationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = User.objects.filter(
            verification_token=serializer.validated_data["token"]
        ).first()

        if not user or user.is_verified:
            return Response(
                {"detail": "Invalid or expired token"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        user.is_verified = True
        user.verification_token = None
        user.save()

        return Response({"detail": "Email successfully verified"})

    @swagger_auto_schema(
        operation_description="Запрос на сброс пароля",
        request_body=PasswordResetRequestSerializer,
        responses={
            200: openapi.Response(
                description="Ссылка для сброса отправлена",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "detail": openapi.Schema(
                            type=openapi.TYPE_STRING, description="Сообщение об успехе"
                        )
                    },
                ),
            ),
            400: "Неверный email",
        },
    )
    @action(detail=False, methods=["post"], permission_classes=[permissions.AllowAny])
    def password_reset(self, request):
        serializer = PasswordResetRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = User.objects.filter(email=serializer.validated_data["email"]).first()
        if user:
            self._send_password_reset_email(user)

        return Response(
            {"detail": "If the email exists, a reset link has been sent"},
            status=status.HTTP_200_OK,
        )

    @swagger_auto_schema(
        operation_description="Подтверждение сброса пароля",
        request_body=PasswordResetConfirmSerializer,
        responses={
            200: openapi.Response(
                description="Пароль изменен",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "detail": openapi.Schema(
                            type=openapi.TYPE_STRING, description="Сообщение об успехе"
                        )
                    },
                ),
            ),
            400: "Неверный или просроченный токен",
        },
    )
    @action(detail=False, methods=["post"], permission_classes=[permissions.AllowAny])
    def password_reset_confirm(self, request):
        serializer = PasswordResetConfirmSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = User.objects.filter(
            verification_token=serializer.validated_data["token"]
        ).first()

        if not user:
            return Response(
                {"detail": "Invalid or expired token"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        user.set_password(serializer.validated_data["new_password"])
        user.verification_token = None
        user.save()

        return Response({"detail": "Password has been reset successfully"})

    def _send_verification_email(self, user):
        subject = "Verify your email"
        verification_url = (
            f"https://yourdomain.com/verify-email/?token={user.verification_token}"
        )
        message = render_to_string(
            "email_verification.html",
            {"user": user, "verification_url": verification_url},
        )
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [user.email],
        )

    def _send_password_reset_email(self, user):
        subject = "Password Reset Request"
        reset_url = (
            f"https://yourdomain.com/reset-password/?token={user.verification_token}"
        )
        message = render_to_string(
            "password_reset_email.html", {"user": user, "reset_url": reset_url}
        )
        send_mail(subject, message, "noreply@yourdomain.com", [user.email])
