import pytest
from rest_framework import status
from rest_framework.test import APIClient

from autodealer_backend.dealers.tests.factories import DealerFactory
from autodealer_backend.users.tests.factories import UserFactory


@pytest.mark.django_db
class TestDealerAPI:
    @pytest.fixture(autouse=True)
    def setup(self):
        self.client = APIClient()
        self.user = UserFactory()
        self.dealer1 = DealerFactory(
            name='Best Cars',
            location='US',
            balance=100000.00,
            is_active=True
        )
        self.dealer2 = DealerFactory(
            name='Auto World',
            location='DE',
            balance=50000.00,
            is_active=False
        )

    def _get_results(self, response):
        return response.data['results'] if 'results' in response.data else response.data

    def test_get_dealer_list(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.get('/api/dealers/')
        assert response.status_code == status.HTTP_200_OK
        results = self._get_results(response)
        assert len(results) >= 2

    def test_filter_by_location(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.get('/api/dealers/?location=US')
        assert response.status_code == status.HTTP_200_OK
        results = self._get_results(response)
        assert any(d['location'] == 'US' for d in results)

    def test_filter_by_balance(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.get('/api/dealers/?balance__gt=75000')
        assert response.status_code == status.HTTP_200_OK
        results = self._get_results(response)
        assert all(float(d['balance']) > 75000 for d in results)

    def test_filter_active(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.get('/api/dealers/?is_active=true')
        assert response.status_code == status.HTTP_200_OK
        results = self._get_results(response)
        assert all(d['is_active'] is True for d in results)

    def test_search_by_name(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.get('/api/dealers/?search=Best')
        assert response.status_code == status.HTTP_200_OK
        results = self._get_results(response)
        assert any('Best' in d['name'] for d in results)
