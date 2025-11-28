import random
from datetime import timedelta

import factory
from django.utils import timezone
from faker import Faker

from autodealer_backend.dealers.tests.factories.dealer_factory import DealerFactory
from autodealer_backend.promotion.models.promotion_model import Promotion

fake = Faker("ru_RU")


class PromotionFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Promotion

    name = factory.LazyFunction(lambda: fake.catch_phrase())
    description = factory.LazyFunction(lambda: fake.text(max_nb_chars=200))
    promotion_type = factory.LazyFunction(lambda: random.choice(["supplier", "dealer"]))
    start_date = factory.LazyFunction(
        lambda: timezone.now() - timedelta(days=random.randint(1, 10))
    )
    end_date = factory.LazyFunction(
        lambda: timezone.now() + timedelta(days=random.randint(10, 30))
    )
    discount_percent = factory.LazyFunction(lambda: random.randint(5, 30))
    max_discount_amount = factory.LazyFunction(
        lambda: (
            round(random.uniform(1000.0, 10000.0), 2)
            if random.choice([True, False])
            else None
        )
    )
    dealer = factory.SubFactory(DealerFactory)
    is_active = True

    @classmethod
    def _create(cls, model_class, *args, **kwargs):
        if kwargs.get("promotion_type") == "supplier":
            kwargs["dealer"] = None
        return super()._create(model_class, *args, **kwargs)
