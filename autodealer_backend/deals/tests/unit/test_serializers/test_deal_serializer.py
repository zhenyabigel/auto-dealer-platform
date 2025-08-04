from decimal import Decimal

import pytest

from autodealer_backend.deals.serializers import DealSerializer
from autodealer_backend.deals.tests.factories import DealFactory


@pytest.mark.django_db
class TestDealSerializer:
    @pytest.fixture
    def deal(self):
        return DealFactory()

    @pytest.fixture
    def valid_data(self, deal):
        return {
            'customer': deal.customer.id,
            'dealer': deal.dealer.id,
            'car': deal.car.id,
            'price': '30000.00',
            'is_active': True
        }

    def test_serialize_deal(self, deal):
        serializer = DealSerializer(deal)
        assert serializer.data['id'] == deal.id
        assert serializer.data['customer'] == deal.customer.id
        assert float(serializer.data['price']) == float(deal.price)

    def test_valid_data(self, valid_data):
        serializer = DealSerializer(data=valid_data)
        assert serializer.is_valid()
        assert serializer.validated_data['price'] == Decimal('30000.00')

    def test_invalid_price(self, valid_data):
        valid_data['price'] = '-100.00'
        serializer = DealSerializer(data=valid_data)
        assert not serializer.is_valid()
        assert 'price' in serializer.errors

    def test_missing_required_fields(self):
        serializer = DealSerializer(data={'price': '10000.00'})
        assert not serializer.is_valid()
        assert 'customer' in serializer.errors
        assert 'dealer' in serializer.errors
        assert 'car' in serializer.errors
