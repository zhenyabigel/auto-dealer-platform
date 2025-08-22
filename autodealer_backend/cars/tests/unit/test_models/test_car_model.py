import pytest
from django.db import IntegrityError

from autodealer_backend.cars.tests.factories.car_model_factory import CarModelFactory


@pytest.mark.django_db
class TestCarModel:
    def test_create_car_model(self):
        car_model = CarModelFactory()
        assert car_model.id is not None
        assert car_model.brand is not None
        assert car_model.model is not None
        assert car_model.is_active is True

    def test_car_model_str(self):
        car_model_no_generation = CarModelFactory(
            brand="BMW", model="X5", generation=""
        )
        assert str(car_model_no_generation) == "BMW X5"

    def test_car_model_unique_constraint(self):
        CarModelFactory(brand="Toyota", model="Camry", generation="XV70")

        with pytest.raises(IntegrityError):
            CarModelFactory(brand="Toyota", model="Camry", generation="XV70")

    def test_car_model_body_types(self):
        car_model = CarModelFactory()
        assert isinstance(car_model.body_types, list)
        assert len(car_model.body_types) > 0
        assert all(isinstance(bt, str) for bt in car_model.body_types)

    def test_car_model_validation(self):
        car_model = CarModelFactory(production_start=2020, production_end=2019)

        assert car_model.production_start == 2020
        assert car_model.production_end == 2019
