import random

import factory
from django.contrib.auth import get_user_model
from django_countries import countries
from faker import Faker

from autodealer_backend.users.models import Customer

fake = Faker("ru_RU")


class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = get_user_model()
        django_get_or_create = ('email',)
        skip_postgeneration_save = True

    email = factory.LazyAttribute(lambda o: f"{fake.user_name()}@example.com")
    username = factory.LazyAttribute(lambda o: o.email.split('@')[0])
    first_name = factory.LazyFunction(lambda: fake.first_name())
    last_name = factory.LazyFunction(lambda: fake.last_name())
    phone = factory.LazyFunction(lambda: fake.phone_number()[:20])
    is_verified = True

    @factory.post_generation
    def password(self, create, extracted, **kwargs):
        self.set_password(extracted or 'testpass123')


class CustomerFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Customer

    user = factory.SubFactory(UserFactory)
    balance = factory.LazyFunction(lambda: fake.pydecimal(
        left_digits=8,
        right_digits=2,
        positive=True
    ))
    address = factory.LazyFunction(lambda: fake.address())
    country = factory.LazyFunction(lambda: random.choice(list(dict(countries).keys())))
