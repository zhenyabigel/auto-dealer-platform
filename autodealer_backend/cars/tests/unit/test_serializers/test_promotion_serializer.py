import pytest

from autodealer_backend.cars.serializers import PromotionSerializer
from autodealer_backend.cars.tests.factories import PromotionFactory


@pytest.mark.django_db
class TestPromotionSerializer:
    @pytest.fixture
    def promotion(self):
        return PromotionFactory()

    @pytest.fixture
    def serializer(self, promotion):
        return PromotionSerializer(promotion)

    def test_serializer_contains_expected_fields(self, serializer):
        data = serializer.data
        assert set(data.keys()) == {
            "id",
            "name",
            "description",
            "start_date",
            "end_date",
            "discount_percent",
            "dealer",
            "cars",
            "is_active",
            "created_at",
            "updated_at",
        }

    def test_serializer_field_values(self, serializer, promotion):
        data = serializer.data
        assert data["name"] == promotion.name
        assert data["description"] == promotion.description
        assert data["discount_percent"] == promotion.discount_percent
        assert data["is_active"] == promotion.is_active
        assert data["dealer"] == promotion.dealer.id
        assert set(data["cars"]) == {car.id for car in promotion.cars.all()}

    def test_date_fields_format(self, serializer):
        data = serializer.data
        assert "T" in data["start_date"]
        assert "T" in data["end_date"]
        assert data["start_date"] < data["end_date"]
