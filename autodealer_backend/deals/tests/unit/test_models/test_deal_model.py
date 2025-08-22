import pytest

from autodealer_backend.deals.tests.factories.deals_factory import DealFactory
from autodealer_backend.deals.tests.factories.offer_factory import OfferFactory
from autodealer_backend.users.tests.factories.user_factory import CustomerUserFactory


@pytest.mark.django_db
class TestDealModel:
    def test_str_method(self):
        deal = DealFactory(deal_type="sale")
        assert str(deal) == f"Сделка #{deal.id} (Продажа клиенту)"

    def test_save_sets_customer_for_sale_deal(self):
        customer = CustomerUserFactory()
        offer = OfferFactory(customer=customer)
        deal = DealFactory(deal_type="sale", offer=offer, customer=None)
        deal.save()
        assert deal.customer == customer

    def test_save_does_not_override_existing_customer(self):
        customer1 = CustomerUserFactory()
        customer2 = CustomerUserFactory()
        offer = OfferFactory(customer=customer1)
        deal = DealFactory(deal_type="sale", offer=offer, customer=customer2)
        deal.save()
        assert deal.customer == customer2
