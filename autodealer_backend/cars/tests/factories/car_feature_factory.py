import random

import factory
from faker import Faker

from autodealer_backend.cars.models import CarFeature
from autodealer_backend.cars.tests.factories.car_model_factory import CarModelFactory

fake = Faker("ru_RU")


class CarFeatureFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = CarFeature
        skip_postgeneration_save = True

    # Убедимся, что CarModel создается
    car_model = factory.SubFactory(CarModelFactory)
    category = factory.LazyFunction(
        lambda: random.choice(
            ["safety", "comfort", "multimedia", "exterior", "interior"]
        )
    )
    name = factory.LazyFunction(
        lambda: random.choice(
            [
                "ABS",
                "ESP",
                "Климат-контроль",
                "Подогрев сидений",
                "Навигация",
                "Apple CarPlay",
                "Светодиодные фары",
                "Кожаный салон",
                "Парктроник",
            ]
        )
    )
    description = factory.LazyFunction(lambda: fake.sentence())
    is_standard = factory.LazyFunction(lambda: random.choice([True, False]))
    is_optional = factory.LazyAttribute(lambda o: not o.is_standard)
