import pytest
from rest_framework.exceptions import ValidationError

from autodealer_backend.users.serializers import UserSerializer


@pytest.mark.django_db
class TestUserSerializer:
    def test_valid_data(self):
        data = {
            'email': 'test@example.com',
            'username': 'testuser',
            'password': 'complexpass123',
            'password2': 'complexpass123',
            'phone': '+1234567890'
        }
        serializer = UserSerializer(data=data)
        assert serializer.is_valid()
        user = serializer.save()
        assert user.email == 'test@example.com'

    def test_passwords_mismatch(self):
        data = {
            'email': 'test@example.com',
            'username': 'testuser',
            'password': 'complexpass123',
            'password2': 'differentpass'
        }
        serializer = UserSerializer(data=data)
        with pytest.raises(ValidationError) as exc:
            serializer.is_valid(raise_exception=True)
        assert 'Пароли не совпадают' in str(exc.value)

    def test_weak_password(self):
        data = {
            'email': 'test@example.com',
            'username': 'testuser',
            'password': '123',
            'password2': '123'
        }
        serializer = UserSerializer(data=data)
        assert not serializer.is_valid()
        assert 'password' in serializer.errors
