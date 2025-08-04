import pytest

from autodealer_backend.cars.serializers import SupplierSerializer
from autodealer_backend.cars.tests.factories import SupplierFactory


@pytest.mark.django_db
class TestSupplierSerializer:
    @pytest.fixture
    def supplier(self):
        return SupplierFactory()

    @pytest.fixture
    def serializer(self, supplier):
        return SupplierSerializer(supplier)

    def test_serializer_contains_expected_fields(self, serializer):
        data = serializer.data
        assert set(data.keys()) == {
            "id",
            "name",
            "year_established",
            "discount_for_dealers",
            "is_active",
            "created_at",
            "updated_at",
        }

    def test_serializer_field_values(self, serializer, supplier):
        data = serializer.data
        assert data["name"] == supplier.name
        assert data["year_established"] == supplier.year_established
        assert data["discount_for_dealers"] == supplier.discount_for_dealers
        assert data["is_active"] == supplier.is_active

    def test_numeric_fields(self, serializer):
        data = serializer.data
        assert isinstance(data["year_established"], int)
        assert isinstance(data["discount_for_dealers"], int)
