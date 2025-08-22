import pytest

from autodealer_backend.dealers.tests.factories.dealer_stock_factory import (
    DealerStockFactory,
)
from autodealer_backend.deals.serializers import DealSerializer
from autodealer_backend.users.tests.factories.user_factory import DealerUserFactory


@pytest.mark.django_db
class TestDealSerializer:
    def test_serializer_valid_sale_deal(self):
        dealer = DealerUserFactory()
        dealer_stock = DealerStockFactory(dealer=dealer.dealer_profile)

        data = {
            "deal_type": "sale",
            "dealer_stock_id": dealer_stock.id,
            "price": "25000.00",
            "quantity": 1,
        }

        serializer = DealSerializer(data=data)
        assert serializer.is_valid() is True

    def test_serializer_sale_deal_without_stock(self):
        data = {"deal_type": "sale", "price": "25000.00", "quantity": 1}

        serializer = DealSerializer(data=data)
        assert serializer.is_valid() is False
        assert "dealer_stock" in str(serializer.errors)

    def test_serializer_purchase_deal_without_supplier_offer(self):
        data = {"deal_type": "purchase", "price": "20000.00", "quantity": 1}

        serializer = DealSerializer(data=data)
        assert serializer.is_valid() is False
        assert "supplier_offer" in str(serializer.errors)

    def test_serializer_sold_car_validation(self):
        dealer = DealerUserFactory()
        dealer_stock = DealerStockFactory(dealer=dealer.dealer_profile, is_sold=True)

        data = {
            "deal_type": "sale",
            "dealer_stock_id": dealer_stock.id,
            "price": "25000.00",
            "quantity": 1,
        }

        serializer = DealSerializer(data=data)
        assert serializer.is_valid() is False
        assert "Этот автомобиль уже продан" in str(serializer.errors)
