import pytest
from django.core.exceptions import ValidationError

from autodealer_backend.cars.tests.factories import SupplierFactory


@pytest.mark.django_db
class TestSupplierModel:
    @pytest.fixture
    def supplier(self):
        return SupplierFactory()

    def test_supplier_creation(self, supplier):
        assert supplier.name is not None
        assert 1900 <= supplier.year_established <= 2023
        assert 0 <= supplier.discount_for_dealers <= 100
        assert supplier.is_active is True

    def test_discount_validation(self):
        with pytest.raises(ValidationError):
            supplier_test = SupplierFactory.build(discount_for_dealers=-10)
            supplier_test.full_clean()
