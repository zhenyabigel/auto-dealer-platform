import factory
from faker import Faker

from autodealer_backend.suppliers.models import Supplier
from autodealer_backend.users.tests.factories.user_factory import SupplierUserFactory

fake = Faker("ru_RU")


class SupplierFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Supplier
        skip_postgeneration_save = True

    user = factory.SubFactory(SupplierUserFactory)
    name = factory.LazyFunction(lambda: fake.company())
    legal_name = factory.LazyFunction(lambda: fake.company() + " LLC")
    supplier_type = factory.LazyFunction(
        lambda: fake.random_element(["official", "parallel", "used"])
    )
    year_established = factory.LazyFunction(lambda: fake.random_int(min=1990, max=2020))
    country = factory.LazyFunction(lambda: fake.country_code())
    city = factory.LazyFunction(lambda: fake.city())
    address = factory.LazyFunction(lambda: fake.address())
    phone = factory.LazyFunction(lambda: fake.phone_number())
    email = factory.LazyFunction(lambda: fake.email())
    website = factory.LazyFunction(lambda: fake.url())
    contact_person = factory.LazyFunction(lambda: fake.name())
    average_delivery_time = 14
    discount_for_dealers = factory.LazyFunction(lambda: fake.random_int(min=0, max=15))
    is_active = True
