import pytest
from django.db import IntegrityError

from autodealer_backend.cars.tests.factories.car_feature_factory import (
    CarFeatureFactory,
)
from autodealer_backend.cars.tests.factories.car_model_factory import CarModelFactory


@pytest.mark.django_db
class TestCarFeature:
    def test_create_car_feature(self):
        feature = CarFeatureFactory()
        assert feature.id is not None
        assert feature.car_model is not None
        assert feature.name is not None

    def test_car_feature_str(self):
        car_model = CarModelFactory(brand="Toyota", model="Camry")
        feature = CarFeatureFactory(car_model=car_model, name="Навигация")
        assert str(feature) == "Toyota Camry: Навигация"

    def test_car_feature_unique_constraint(self):
        car_model = CarModelFactory()
        CarFeatureFactory(car_model=car_model, name="ABS")

        with pytest.raises(IntegrityError):
            CarFeatureFactory(car_model=car_model, name="ABS")

    def test_car_feature_category_choices(self):
        feature = CarFeatureFactory()
        assert feature.category in [
            "safety",
            "comfort",
            "multimedia",
            "exterior",
            "interior",
        ]

    def test_car_feature_optional_standard_logic(self):
        feature_standard = CarFeatureFactory(is_standard=True)
        assert feature_standard.is_standard is True
        assert feature_standard.is_optional is False

        feature_optional = CarFeatureFactory(is_standard=False)
        assert feature_optional.is_standard is False
        assert feature_optional.is_optional is True
