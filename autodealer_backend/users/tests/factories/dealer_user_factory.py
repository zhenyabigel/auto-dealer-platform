import factory
from django.contrib.auth import get_user_model
from faker import Faker

User = get_user_model()
fake = Faker("ru_RU")


class DealerUserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User
        skip_postgeneration_save = True

    email = factory.LazyFunction(lambda: fake.unique.email())
    username = factory.LazyFunction(lambda: fake.unique.user_name())
    phone = factory.LazyFunction(lambda: fake.phone_number())
    address = factory.LazyFunction(lambda: fake.address())
    country = factory.LazyFunction(lambda: fake.country_code())
    balance = factory.LazyFunction(
        lambda: factory.faker.faker.Faker().pydecimal(
            left_digits=6, right_digits=2, positive=True
        )
    )
    is_verified = True
    verification_token = None
    role = "dealer"
    password = factory.PostGenerationMethodCall("set_password", "password123")
