import pytest

from autodealer_backend.cars.serializers import CarSerializer
from autodealer_backend.cars.tests.factories import CarFactory


@pytest.mark.django_db
class TestCarSerializer:
    @pytest.fixture
    def car(self):
        return CarFactory()

    @pytest.fixture
    def serializer(self, car):
        return CarSerializer(car)

    def test_serializer_contains_expected_fields(self, serializer):
        data = serializer.data
        assert set(data.keys()) == {
            "id",
            "brand",
            "model",
            "year",
            "engine_type",
            "price",
            "quantity",
            "dealer",
            "supplier",
            "is_active",
            "created_at",
            "updated_at",
        }

    def test_serializer_field_values(self, serializer, car):
        data = serializer.data
        assert data["brand"] == car.brand
        assert float(data["price"]) == float(car.price)
        assert data["model"] == car.model
        assert data["year"] == car.year
        assert data["engine_type"] == car.engine_type
        assert data["is_active"] == car.is_active

    def test_price_decimal_format(self, serializer):
        price_str = serializer.data["price"]
        assert "." in price_str
        assert len(price_str.split(".")[1]) == 2

    def test_foreign_key_relations(self, serializer, car):
        assert serializer.data["dealer"] == car.dealer.id
        assert serializer.data["supplier"] == car.supplier.id
