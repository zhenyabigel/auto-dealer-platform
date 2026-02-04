import pytest

from autodealer_backend.users.serializers import UserSerializer
from autodealer_backend.users.tests.factories.user_factory import UserFactory


@pytest.mark.django_db
class TestUserSerializer:
    def test_serializer_output(self):
        user = UserFactory(
            email="test@example.com",
            username="testuser",
            phone="+1234567890",
            address="123 Main St",
            country="US",
            balance=50000,
            is_verified=True,
        )
        serializer = UserSerializer(user)
        data = serializer.data

        assert data["email"] == "test@example.com"
        assert data["username"] == "testuser"
        assert data["phone"] == "+1234567890"
        assert data["address"] == "123 Main St"
        assert data["country"] == "United States"
        assert data["balance"] == "50000.00"
        assert data["is_verified"] is True
        assert data["role"] == "customer"
        assert data["role_display"] == "Покупатель"

    def test_read_only_fields(self):
        user = UserFactory()
        data = {"is_verified": True, "date_joined": "2020-01-01T00:00:00Z"}
        serializer = UserSerializer(user, data=data, partial=True)
        assert serializer.is_valid()
        updated = serializer.save()
        assert updated.is_verified is False  # Не обновляется
