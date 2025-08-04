import pytest
from rest_framework import status
from rest_framework.test import APIClient

from autodealer_backend.cars.tests.factories import SupplierFactory
from autodealer_backend.users.tests.factories import UserFactory


@pytest.mark.django_db
class TestSupplierAPI:
    @pytest.fixture(autouse=True)
    def setup(self):
        self.client = APIClient()
        self.user = UserFactory()
        self.supplier = SupplierFactory()

    def test_get_supplier_list(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.get('/api/suppliers/')
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) > 0


    def test_filter_suppliers(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.get('/api/suppliers/?year_established__gt=2000')
        assert response.status_code == status.HTTP_200_OK
