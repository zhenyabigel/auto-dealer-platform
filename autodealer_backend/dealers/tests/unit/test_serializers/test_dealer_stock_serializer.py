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

        valid_data = {
            "dealer_id": dealer.id,
            "car_model_id": car_model.id,
            "supplier_id": supplier.id,
            "purchase_price": "25000.00",
            "selling_price": "30000.00",
            "vin": "1HGCM82633A123456",
            "mileage": 0,
            "color": "Black",
            "condition": "new",
            "arrival_date": "2024-01-15",
        }

        serializer = DealerStockSerializer(data=valid_data)
        assert serializer.is_valid(), f"Serializer errors: {serializer.errors}"

        stock_item = serializer.save()
        assert stock_item.dealer == dealer
        assert stock_item.car_model == car_model

    def test_vin_validation_correct_length(self):
        dealer = DealerFactory()
        car_model = CarModelFactory()
        supplier = SupplierFactory()

        valid_data = {
            "dealer_id": dealer.id,
            "car_model_id": car_model.id,
            "supplier_id": supplier.id,
            "purchase_price": "25000.00",
            "selling_price": "30000.00",
            "vin": "1HGCM82633A123456",
            "mileage": 0,
            "arrival_date": "2024-01-15",
        }

        serializer = DealerStockSerializer(data=valid_data)
        assert serializer.is_valid(), f"Serializer errors: {serializer.errors}"

    def test_vin_validation_incorrect_length(self):
        dealer = DealerFactory()
        car_model = CarModelFactory()
        supplier = SupplierFactory()

        invalid_data = {
            "dealer_id": dealer.id,
            "car_model_id": car_model.id,
            "supplier_id": supplier.id,
            "purchase_price": "25000.00",
            "selling_price": "30000.00",
            "vin": "SHORTVIN",
            "arrival_date": "2024-01-15",
        }

        serializer = DealerStockSerializer(data=invalid_data)
        assert not serializer.is_valid()
        assert "vin" in serializer.errors
        assert "17 символов" in str(serializer.errors["vin"])

    def test_price_validation_valid(self):
        dealer = DealerFactory()
        car_model = CarModelFactory()
        supplier = SupplierFactory()

        valid_data = {
            "dealer_id": dealer.id,
            "car_model_id": car_model.id,
            "supplier_id": supplier.id,
            "purchase_price": "25000.00",
            "selling_price": "30000.00",
            "vin": "1HGCM82633A123456",
            "arrival_date": "2024-01-15",
        }

        serializer = DealerStockSerializer(data=valid_data)
        assert serializer.is_valid(), f"Serializer errors: {serializer.errors}"

    def test_price_validation_invalid(self):
        dealer = DealerFactory()
        car_model = CarModelFactory()
        supplier = SupplierFactory()

        invalid_data = {
            "dealer_id": dealer.id,
            "car_model_id": car_model.id,
            "supplier_id": supplier.id,
            "purchase_price": "30000.00",
            "selling_price": "25000.00",
            "vin": "1HGCM82633A123456",
            "arrival_date": "2024-01-15",
        }

        serializer = DealerStockSerializer(data=invalid_data)
        assert not serializer.is_valid()

        has_price_error = False
        for field, errors in serializer.errors.items():
            for error in errors:
                if "Цена продажи не может быть меньше цены покупки" in str(error):
                    has_price_error = True
                    break
        assert has_price_error, "Should have price validation error"
