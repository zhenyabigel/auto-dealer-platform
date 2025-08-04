import pytest
from rest_framework import status
from rest_framework.test import APIClient

from autodealer_backend.deals.tests.factories import OfferFactory
from autodealer_backend.users.tests.factories import UserFactory


@pytest.mark.django_db
class TestOfferAPI:
    @pytest.fixture(autouse=True)
    def setup(self):
        self.client = APIClient()
        self.user = UserFactory()
        self.offer = OfferFactory(customer__user=self.user)

    def test_get_offer_list(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.get("/api/offers/")
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data["results"]) > 0

    def test_filter_by_status(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.get("/api/offers/?status=pending")
        assert response.status_code == status.HTTP_200_OK
        assert all(item["status"] == "pending" for item in response.data["results"])

    def test_create_offer_success(self):
        self.client.force_authenticate(user=self.user)
        data = {
            "customer": self.offer.customer.id,
            "car_model": "Toyota Camry",
            "max_price": "25000.00",
            "status": "pending",
        }
        response = self.client.post("/api/offers/", data, format="json")
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data["car_model"] == data["car_model"]

    def test_create_offer_invalid_data(self):
        self.client.force_authenticate(user=self.user)
        data = {
            "customer": self.offer.customer.id,
            "car_model": "",
            "max_price": "-100.00",
            "status": "invalid_status",
        }
        response = self.client.post("/api/offers/", data, format="json")
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        errors = response.data
        assert "car_model" in errors
        assert "max_price" in errors
        assert "status" in errors
