# В файле suppliers/tests/unit/test_serializers/test_supplier_serializer.py

import pytest

from autodealer_backend.suppliers.models import Supplier
from autodealer_backend.suppliers.serializers import SupplierSerializer
from autodealer_backend.users.tests.factories import UserFactory


@pytest.mark.django_db
class TestSupplierSerializer:
    def test_serializer_valid_data(self):
        data = {
            "name": "Euro Supplier",
            "supplier_type": "official",
            "year_established": 2000,
            "country": "DE",
            "city": "Berlin",
            "address": "Test Address 123",  # Добавлено
            "contact_person": "John Doe",  # Добавлено
            "phone": "+49123456789",
            "email": "contact@euro.com",
        }
        serializer = SupplierSerializer(data=data)
        assert serializer.is_valid(), serializer.errors
        assert serializer.validated_data["name"] == "Euro Supplier"

    def test_serializer_create(self):
        user = UserFactory(role="supplier")
        data = {
            "user": user.id,
            "name": "New Supplier",
            "supplier_type": "parallel",
            "year_established": 2010,
            "country": "US",
            "city": "Miami",
            "address": "Test Address 456",  # Добавлено
            "contact_person": "Jane Smith",  # Добавлено
            "phone": "+1234567890",
            "email": "contact@new.com",
        }
        serializer = SupplierSerializer(data=data)
        assert serializer.is_valid()
        supplier = serializer.save()
        assert Supplier.objects.count() == 1
        assert supplier.name == "New Supplier"

    def test_future_year_validation(self):
        data = {
            "name": "Future Co",
            "supplier_type": "official",
            "year_established": 2500,  # Будущий год
            "country": "RU",
            "city": "Moscow",
            "address": "Test Address 789",  # Добавлено
            "contact_person": "Test Person",  # Добавлено
            "phone": "+79991234567",
            "email": "test@test.com",
        }
        serializer = SupplierSerializer(data=data)
        assert not serializer.is_valid()
        assert "year_established" in serializer.errors
