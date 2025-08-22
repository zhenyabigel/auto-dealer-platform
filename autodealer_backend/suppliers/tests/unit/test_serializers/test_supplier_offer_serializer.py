import pytest

from autodealer_backend.cars.tests.factories import CarModelFactory
from autodealer_backend.suppliers.serializers import SupplierOfferSerializer
from autodealer_backend.suppliers.tests.factories.supplier_factory import (  # Исправлено
    SupplierFactory,
)


@pytest.mark.django_db
class TestSupplierOfferSerializer:
    def test_serializer_valid_data(self):
        supplier = SupplierFactory()
        car_model = CarModelFactory()
        data = {
            "supplier_id": supplier.id,  # Теперь это ID Supplier, а не User
            "car_model_id": car_model.id,
            "price": "20000.00",
            "quantity_available": 5,
            "valid_from": "2025-01-01",
            "valid_to": "2025-02-01",
        }
        serializer = SupplierOfferSerializer(data=data)
        assert serializer.is_valid(), serializer.errors

    def test_raw_fields_validation(self):
        supplier = SupplierFactory()
        data = {
            "supplier_id": supplier.id,
            "raw_brand": "Tesla",
            "raw_model": "Model 3",
            "price": "35000",
            "quantity_available": 1,
            "valid_from": "2025-01-01",
            "valid_to": "2025-02-01",
        }
        serializer = SupplierOfferSerializer(data=data)
        assert serializer.is_valid()

    def test_missing_car_and_raw(self):
        supplier = SupplierFactory()
        data = {
            "supplier_id": supplier.id,
            "price": "20000",
            "quantity_available": 1,
            "valid_from": "2025-01-01",
            "valid_to": "2025-02-01",
        }
        serializer = SupplierOfferSerializer(data=data)
        assert not serializer.is_valid()
        assert "non_field_errors" in serializer.errors
