import pytest
from rest_framework import status
from rest_framework.test import APIClient

from autodealer_backend.deals.tests.factories import DealFactory
from autodealer_backend.users.tests.factories import UserFactory


@pytest.mark.django_db
class TestDealAPI:
    @pytest.fixture(autouse=True)
    def setup(self):
        self.client = APIClient()
        self.user = UserFactory()
        self.deal = DealFactory(customer__user=self.user)

    def test_get_deal_list(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.get('/api/deals/')
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) > 0

    def test_filter_by_dealer(self):
        self.client.force_authenticate(user=self.user)
        dealer_id = self.deal.dealer.id
        response = self.client.get(f'/api/deals/?dealer={dealer_id}')
        assert response.status_code == status.HTTP_200_OK
        assert all(item['dealer'] == dealer_id
                   for item in response.data['results'])

    def test_create_deal_success(self):
        self.client.force_authenticate(user=self.user)
        data = {
            'customer': self.deal.customer.id,
            'dealer': self.deal.dealer.id,
            'car': self.deal.car.id,
            'price': '30000.00'
        }
        response = self.client.post('/api/deals/', data, format='json')
        assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED

    def test_create_deal_invalid_price(self):
        self.client.force_authenticate(user=self.user)
        data = {
            'customer': self.deal.customer.id,
            'dealer': self.deal.dealer.id,
            'car': self.deal.car.id,
            'price': '-100.00'
        }
        response = self.client.post('/api/deals/', data, format='json')
        assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED

