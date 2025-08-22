import factory
from django.contrib.auth import get_user_model
from faker import Faker

User = get_user_model()
fake = Faker("ru_RU")


class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User
        skip_postgeneration_save = True

    email = factory.LazyFunction(lambda: fake.email())
    username = factory.LazyFunction(lambda: fake.user_name())
    phone = factory.LazyFunction(lambda: fake.phone_number())
    address = factory.LazyFunction(lambda: fake.address())
    country = factory.LazyFunction(lambda: fake.country_code())
    balance = factory.LazyFunction(
        lambda: fake.pydecimal(left_digits=6, right_digits=2, positive=True)
    )
    is_verified = False
    verification_token = factory.LazyFunction(lambda: fake.sha256())
    role = "customer"
    password = factory.PostGenerationMethodCall("set_password", "password123")

    @factory.post_generation
    def make_verified(self, create, extracted, **kwargs):
        if extracted:
            self.is_verified = True
            self.verification_token = None
            self.save()


# Удобные алиасы для разных ролей
class CustomerUserFactory(UserFactory):
    role = "customer"


class DealerUserFactory(UserFactory):
    role = "dealer"


class SupplierUserFactory(UserFactory):
    role = "supplier"


class AdminUserFactory(UserFactory):
    role = "admin"
    is_staff = True
    is_superuser = True
