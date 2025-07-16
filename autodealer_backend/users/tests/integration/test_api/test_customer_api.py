import pytest
from rest_framework import status
from rest_framework.test import APIClient

from autodealer_backend.users.tests.factories import UserFactory, CustomerFactory


@pytest.mark.django_db
class TestCustomerAPI:
    @pytest.fixture(autouse=True)
    def setup(self):
        self.client = APIClient()
        self.user = UserFactory()
        self.customer = CustomerFactory(user=self.user)
        self.client.force_authenticate(user=self.user)

    def test_get_customer_list_admin_only(self):
        response = self.client.get('/api/customers/')
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_get_my_customer_profile(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.get('/api/customers/me/')
        assert response.status_code == status.HTTP_200_OK
        assert response.data['user']['email'] == self.user.email

    def test_filter_by_country(self):
        admin = UserFactory(is_staff=True)
        self.client.force_authenticate(user=admin)

        CustomerFactory(country='US')
        CustomerFactory(country='GB')

        response = self.client.get('/api/customers/?country=US')
        assert response.status_code == status.HTTP_200_OK
        assert all(c['country'] == 'US' for c in response.data['results'])
