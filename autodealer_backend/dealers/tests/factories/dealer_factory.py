from decimal import Decimal

import factory
from faker import Faker
from users.tests.factories.dealer_user_factory import DealerUserFactory

from autodealer_backend.dealers.models import Dealer

fake = Faker("ru_RU")


class DealerFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Dealer
        skip_postgeneration_save = True

    user = factory.SubFactory(DealerUserFactory)
    name = factory.LazyFunction(lambda: fake.unique.company())
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
                        min_value=1000,
                        max_value=100000,
                    ),
                    2,
                )
            )
        )
    )
    is_active = True

    @factory.post_generation
    def preferred_car_models(self, create, extracted, **kwargs):
        if not create:
            return

        if extracted:
            for car_model in extracted:
                self.preferred_car_models.add(car_model)
