import pytest
from rest_framework import status
from rest_framework.test import APIClient

from autodealer_backend.suppliers.tests.factories.supplier_factory import (
    SupplierFactory,
)
from autodealer_backend.users.tests.factories.user_factory import UserFactory


@pytest.mark.django_db
class TestSupplierAPI:
    @pytest.fixture(autouse=True)
    def setup(self):
        self.client = APIClient()
        self.admin = UserFactory(is_staff=True, is_superuser=True)
        self.supplier_user = UserFactory(role="supplier")
        self.customer = UserFactory(role="customer")
        self.supplier = SupplierFactory(user=self.supplier_user)

    def test_list_suppliers_authenticated(self):
        self.client.force_authenticate(user=self.customer)
        response = self.client.get("/api/suppliers/")
        assert response.status_code == status.HTTP_200_OK
        assert "results" in response.data

    def test_retrieve_supplier_detail(self):
        self.client.force_authenticate(user=self.customer)
        response = self.client.get(f"/api/suppliers/{self.supplier.id}/")
        assert response.status_code == status.HTTP_200_OK
        assert response.data["name"] == self.supplier.name

    def test_create_supplier_admin_only(self):
        self.client.force_authenticate(user=self.customer)
        data = {
            "name": "New Supplier",
            "supplier_type": "official",
            "year_established": 2000,
            "country": "US",
            "city": "LA",
            "phone": "+123",
            "email": "test@test.com",
        }
        response = self.client.post("/api/suppliers/", data)
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_admin_can_create_supplier(self):
        self.client.force_authenticate(user=self.admin)
        user = UserFactory(role="supplier")
        data = {
            "user": user.id,
            "name": "Global Auto",
            "supplier_type": "official",
            "year_established": 2010,
            "country": "DE",
            "city": "Berlin",
            "phone": "+49123",
            "email": "contact@global.com",
        }
        response = self.client.post("/api/suppliers/", data, format="json")
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data["name"] == "Global Auto"
