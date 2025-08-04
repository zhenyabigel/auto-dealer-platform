import pytest
from django.core.exceptions import ValidationError

from autodealer_backend.cars.tests.factories import CarFactory


@pytest.mark.django_db
class TestCarModel:
    @pytest.fixture
    def car(self):
        return CarFactory()

    def test_car_creation(self, car):
        assert car.brand in ["Toyota", "BMW", "Mercedes", "Honda", "Ford"]
        assert car.is_active is True

    def test_invalid_year(self, car):
        car.year = 2050
        car.full_clean()
        car.year = 3000
        with pytest.raises(ValidationError):
            car.full_clean()

    def test_missing_supplier(self):
        car_test = CarFactory(supplier=None)
        with pytest.raises(ValidationError) as excinfo:
            car_test.full_clean()
        assert "supplier" in str(excinfo.value)
