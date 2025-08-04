import pytest

from autodealer_backend.dealers.serializers import DealerSerializer
from autodealer_backend.dealers.tests.factories import DealerFactory


@pytest.mark.django_db
class TestDealerSerializer:
    @pytest.fixture
    def dealer(self):
        return DealerFactory(
            preferred_car_brands=['Toyota', 'BMW'],
            preferred_car_characteristics={'year__gte': 2020}
        )

    @pytest.fixture
    def serializer(self, dealer):
        return DealerSerializer(dealer)

    def test_serializer_contains_expected_fields(self, serializer):
        data = serializer.data
        assert set(data.keys()) == {
            'id', 'name', 'location', 'balance',
            'preferred_car_brands', 'preferred_car_characteristics',
            'is_active', 'created_at', 'updated_at'
        }

    def test_serializer_field_values(self, serializer, dealer):
        data = serializer.data
        assert data['name'] == dealer.name
        assert data['location'] == dealer.location.code
        assert float(data['balance']) == float(dealer.balance)
        assert data['preferred_car_brands'] == dealer.preferred_car_brands
        assert data['preferred_car_characteristics'] == dealer.preferred_car_characteristics
        assert data['is_active'] == dealer.is_active

    def test_balance_decimal_format(self, serializer):
        balance_str = serializer.data['balance']
        assert '.' in balance_str
        assert len(balance_str.split('.')[1]) == 2

    def test_json_fields_format(self, serializer):
        assert isinstance(serializer.data['preferred_car_brands'], list)
        assert isinstance(serializer.data['preferred_car_characteristics'], dict)

    def test_create_validation(self):
        serializer = DealerSerializer(data={
            'name': 'New Dealer',
            'location': 'US',
            'balance': '100000.00',
            'preferred_car_brands': ['Toyota'],
            'preferred_car_characteristics': {'year__gte': 2020}
        })
        assert serializer.is_valid(), serializer.errors

    def test_invalid_data(self):
        serializer = DealerSerializer(data={
            'name': '',
            'balance': '-100.00',
            'preferred_car_brands': "not a list",
            'location': 'INVALID'
        })
        assert not serializer.is_valid()
        errors = serializer.errors
        assert 'name' in errors
        assert 'balance' in errors
        assert 'preferred_car_brands' in errors
        assert 'location' in errors
