import factory
from deals.tests.factories.deals_factory import DealFactory
from faker import Faker

from autodealer_backend.suppliers.tests.factories.supplier_offer_factory import (
    SupplierOfferFactory,
)
from autodealer_backend.users.tests.factories.dealer_user_factory import (
    DealerUserFactory,
)

fake = Faker()


class PurchaseDealFactory(DealFactory):
    deal_type = "purchase"
    dealer = factory.SubFactory(DealerUserFactory)
    supplier_offer = factory.SubFactory(SupplierOfferFactory)
