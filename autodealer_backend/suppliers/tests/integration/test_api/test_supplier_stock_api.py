import pytest
from rest_framework import status
from rest_framework.test import APIClient

from autodealer_backend.cars.tests.factories import CarModelFactory
from autodealer_backend.suppliers.tests.factories.supplier_factory import (
    SupplierFactory,
)
from autodealer_backend.suppliers.tests.factories.supplier_offer_factory import (
    SupplierOfferFactory,
)
from autodealer_backend.users.tests.factories.user_factory import UserFactory


@pytest.mark.django_db
class TestSupplierOfferAPI:
    @pytest.fixture(autouse=True)
    def setup(self):
        self.client = APIClient()
        self.admin = UserFactory(is_staff=True, is_superuser=True)
        self.supplier_user = UserFactory(role="supplier")
        self.customer = UserFactory(role="customer")
        self.supplier = SupplierFactory(user=self.supplier_user)
        self.car_model = CarModelFactory()
        self.offer = SupplierOfferFactory(
            supplier=self.supplier, car_model=self.car_model
        )

    def test_list_offers_authenticated(self):
        self.client.force_authenticate(user=self.customer)
        response = self.client.get("/api/supplier-offer/")
        assert response.status_code == status.HTTP_200_OK

    def test_filter_by_supplier(self):
        SupplierOfferFactory(supplier=SupplierFactory())
        self.client.force_authenticate(user=self.customer)
        response = self.client.get(f"/api/supplier-offer/?supplier={self.supplier.id}")
        results = response.data["results"]
        assert all(item["supplier"] == self.supplier.id for item in results)
