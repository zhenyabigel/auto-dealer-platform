import pytest

from autodealer_backend.users.models import User
from autodealer_backend.users.serializers import (
    CustomTokenObtainPairSerializer,
    EmailVerificationSerializer,
    PasswordResetConfirmSerializer,
    PasswordResetRequestSerializer,
    UserRegistrationSerializer,
)
from autodealer_backend.users.tests.factories import UserFactory


@pytest.mark.django_db
class TestUserRegistrationSerializer:
    def test_passwords_must_match(self):
        data = {
            "email": "new@example.com",
            "username": "newuser",
            "password": "pass123",
            "password2": "pass456",
            "phone": "+123",
        }
        serializer = UserRegistrationSerializer(data=data)
        assert not serializer.is_valid()
        assert "Passwords don't match" in str(serializer.errors)

    def test_create_user_success(self):
        data = {
            "email": "new@example.com",
            "username": "newuser",
            "password": "pass123",
            "password2": "pass123",
            "phone": "+123",
        }
        serializer = UserRegistrationSerializer(data=data)
        assert serializer.is_valid()
        user = serializer.save()
        assert User.objects.count() == 1
        assert user.check_password("pass123")
        assert user.verification_token is not None


class TestCustomTokenObtainPairSerializer:
    def test_token_includes_custom_claims(self):
        user = UserFactory()
        serializer = CustomTokenObtainPairSerializer()
        serializer.user = user
        data = serializer.validate({"email": user.email, "password": "password123"})
        assert "id" in data
        assert "email" in data
        assert "role" in data
        assert "is_verified" in data
        assert data["email"] == user.email
        assert data["role"] == "customer"


class TestEmailVerificationSerializer:
    def test_token_required(self):
        serializer = EmailVerificationSerializer(data={})
        assert not serializer.is_valid()
        assert "token" in serializer.errors


class TestPasswordResetRequestSerializer:
    def test_email_required(self):
        serializer = PasswordResetRequestSerializer(data={})
        assert not serializer.is_valid()
        assert "email" in serializer.errors


class TestPasswordResetConfirmSerializer:
    def test_passwords_must_match(self):
        data = {
            "token": "abc123",
            "new_password": "newpass",
            "new_password2": "mismatch",
        }
        serializer = PasswordResetConfirmSerializer(data=data)
        assert not serializer.is_valid()
        assert "Passwords don't match" in str(serializer.errors)
