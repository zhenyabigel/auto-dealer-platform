import pytest
from django.db import IntegrityError

from autodealer_backend.promotion.models.promotion_car_model import PromotionCar
from autodealer_backend.promotion.tests.factories.promotion_car_factory import (
    PromotionCarFactory,
)


@pytest.mark.django_db
class TestPromotionCarModel:

    def test_promotion_car_creation(self):
        promotion_car = PromotionCarFactory()
        assert promotion_car.promotion is not None
        assert promotion_car.car_model is not None

    def test_promotion_car_unique_together(self):
        promotion_car = PromotionCarFactory()

        with pytest.raises(IntegrityError):
            PromotionCarFactory(
                promotion=promotion_car.promotion, car_model=promotion_car.car_model
            )

    def test_meta_verbose_names(self):
        assert PromotionCar._meta.verbose_name == "Автомобиль в акции"
        assert PromotionCar._meta.verbose_name_plural == "Автомобили в акциях"

    def test_db_table_name(self):
        assert PromotionCar._meta.db_table == "promotion_car_relations"
