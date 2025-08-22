from decimal import Decimal

import factory
from faker import Faker

from autodealer_backend.dealers.models import Dealer
from autodealer_backend.users.tests.factories.user_factory import DealerUserFactory

fake = Faker("ru_RU")


class DealerFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Dealer
        skip_postgeneration_save = True

    user = factory.SubFactory(DealerUserFactory)
    name = factory.LazyFunction(lambda: fake.company())
    legal_name = factory.LazyFunction(lambda: fake.company() + " LLC")
    dealer_type = factory.LazyFunction(
        lambda: fake.random_element(["premium", "standard", "discount"])
    )
    location = factory.LazyFunction(lambda: fake.country_code())
    address = factory.LazyFunction(lambda: fake.address())
    phone = factory.LazyFunction(lambda: fake.phone_number())
    email = factory.LazyFunction(lambda: fake.email())
    website = factory.LazyFunction(lambda: fake.url())
    contact_person = factory.LazyFunction(lambda: fake.name())

    balance = factory.LazyFunction(
        lambda: Decimal(
            str(
                round(
                    fake.pydecimal(
                        left_digits=6,
                        right_digits=2,
                        positive=True,
                        min_value=0.01,
                        max_value=100000,
                    ),
                    2,
                )
            )
        )
    )

    is_active = True
