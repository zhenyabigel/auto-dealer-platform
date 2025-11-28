import random

import factory
from faker import Faker

from autodealer_backend.cars.tests.factories import CarModelFactory
from autodealer_backend.promotion.models.promotion_car_model import PromotionCar
from autodealer_backend.promotion.tests.factories.promotion_factory import (
    PromotionFactory,
)

fake = Faker("ru_RU")


class PromotionCarFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = PromotionCar

    promotion = factory.SubFactory(PromotionFactory)
    car_model = factory.SubFactory(CarModelFactory)
    special_price = factory.LazyFunction(
        lambda: (
            round(random.uniform(500000.0, 3000000.0), 2)
            if random.choice([True, False, False])
            else None
        )
    )
