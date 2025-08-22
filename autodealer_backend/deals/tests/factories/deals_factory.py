from decimal import Decimal

import factory
from faker import Faker

from autodealer_backend.deals.models.deal_model import Deal

fake = Faker()


class DealFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Deal
        skip_postgeneration_save = True

    deal_type = "sale"
    price = factory.LazyFunction(
        lambda: Decimal(
            str(fake.pydecimal(left_digits=6, right_digits=2, positive=True))
        )
    )
    quantity = 1
    is_completed = False
