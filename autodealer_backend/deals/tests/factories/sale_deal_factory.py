import factory
from deals.tests.factories.deals_factory import DealFactory
from faker import Faker

from autodealer_backend.dealers.tests.factories.dealer_stock_factory import (
    DealerStockFactory,
)
from autodealer_backend.deals.tests.factories.offer_factory import OfferFactory
from autodealer_backend.users.tests.factories.customer_user_factory import (
    CustomerUserFactory,
)

fake = Faker()


class SaleDealFactory(DealFactory):
    deal_type = "sale"
    customer = factory.SubFactory(CustomerUserFactory)
    dealer_stock = factory.SubFactory(DealerStockFactory)
    offer = factory.SubFactory(
        OfferFactory, customer=factory.SelfAttribute("..customer")
    )
