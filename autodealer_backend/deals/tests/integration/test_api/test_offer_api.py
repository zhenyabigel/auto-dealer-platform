import pytest
from rest_framework import status
from rest_framework.test import APIClient

from autodealer_backend.cars.tests.factories.car_model_factory import CarModelFactory
from autodealer_backend.deals.tests.factories.offer_factory import OfferFactory
from autodealer_backend.users.tests.factories.user_factory import (
    AdminUserFactory,
    CustomerUserFactory,
    DealerUserFactory,
)


@pytest.mark.django_db
class TestOfferAPI:
    @pytest.fixture(autouse=True)
    def setup(self):
        self.client = APIClient()
        self.customer = CustomerUserFactory()
        self.dealer = DealerUserFactory()
        self.admin = AdminUserFactory()
        self.car_model = CarModelFactory()
        self.offer = OfferFactory(customer=self.customer, car_model=self.car_model)

    def test_list_offers_authenticated_customer(self):
        self.client.force_authenticate(user=self.customer)
        response = self.client.get("/api/offers/")
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data["results"]) >= 1

    def test_list_offers_unauthenticated(self):
        response = self.client.get("/api/offers/")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_list_offers_dealer_sees_empty(self):
        self.client.force_authenticate(user=self.dealer)
        response = self.client.get("/api/offers/")
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data["results"]) == 0

    def test_list_offers_admin_sees_all(self):
        self.client.force_authenticate(user=self.admin)
        response = self.client.get("/api/offers/")
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data["results"]) >= 1

    def test_create_offer_unauthenticated(self):
        data = {"car_model_id": self.car_model.id, "max_price": "30000.00"}
        response = self.client.post("/api/offers/", data, format="json")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_retrieve_own_offer(self):
        self.client.force_authenticate(user=self.customer)
        response = self.client.get(f"/api/offers/{self.offer.id}/")
        assert response.status_code == status.HTTP_200_OK
        assert response.data["id"] == self.offer.id

    def test_retrieve_other_customer_offer(self):
        other_customer = CustomerUserFactory()
        self.client.force_authenticate(user=other_customer)
        response = self.client.get(f"/api/offers/{self.offer.id}/")
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_update_own_offer(self):
        self.client.force_authenticate(user=self.customer)
        data = {"max_price": "35000.00", "notes": "Updated price"}
        response = self.client.patch(
            f"/api/offers/{self.offer.id}/", data, format="json"
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.data["max_price"] == "35000.00"

    def test_filter_offers_by_car_brand(self):
        self.client.force_authenticate(user=self.customer)
        response = self.client.get(f"/api/offers/?car_brand={self.car_model.brand}")
        assert response.status_code == status.HTTP_200_OK

    def test_filter_active_offers(self):
        self.client.force_authenticate(user=self.customer)
        response = self.client.get("/api/offers/?active=true")
        assert response.status_code == status.HTTP_200_OK
