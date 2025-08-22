import pytest

from autodealer_backend.cars.tests.factories import CarModelFactory
from autodealer_backend.dealers.serializers import DealerStockSerializer
from autodealer_backend.dealers.tests.factories.dealer_factory import DealerFactory
from autodealer_backend.suppliers.tests.factories.supplier_factory import (
    SupplierFactory,
)


@pytest.mark.django_db
class TestDealerStockSerializer:
    def test_serializer_valid_data(self):
        dealer = DealerFactory()
        car_model = CarModelFactory()
        supplier = SupplierFactory()
        data = {
            "dealer": dealer.id,
            "car_model_id": car_model.id,
            "supplier_id": supplier.id,
            "purchase_price": "20000.00",
            "selling_price": "25000.00",
            "vin": "1HGBH41JXMN109186",
            "color": "Red",
            "condition": "new",
            "arrival_date": "2025-01-01",
        }
        serializer = DealerStockSerializer(data=data)
        assert serializer.is_valid(), serializer.errors

    def test_vin_validation(self):
        data = {
            "dealer": DealerFactory().id,
            "car_model_id": CarModelFactory().id,
            "purchase_price": "20000",
            "selling_price": "25000",
            "vin": "SHORT",
            "color": "Red",
            "arrival_date": "2025-01-01",
        }
        serializer = DealerStockSerializer(data=data)
        assert not serializer.is_valid()
        assert "vin" in serializer.errors

    def test_price_validation(self):
        dealer = DealerFactory()
        car_model = CarModelFactory()
        supplier = SupplierFactory()

        data = {
            "dealer": dealer.id,
            "car_model_id": car_model.id,
            "supplier_id": supplier.id,
            "purchase_price": "30000",
            "selling_price": "25000",  # Меньше покупки
            "vin": "1HGBH41JXMN109186",
            "color": "Red",
            "arrival_date": "2025-01-01",
        }
        serializer = DealerStockSerializer(data=data)
        assert not serializer.is_valid()
        assert "non_field_errors" in serializer.errors
        assert "Цена продажи не может быть меньше цены покупки" in str(
            serializer.errors
        )
