import pytest
from rest_framework import status
from rest_framework.test import APIClient

from autodealer_backend.cars.tests.factories import CarFactory
from autodealer_backend.users.tests.factories import UserFactory


@pytest.mark.django_db
class TestCarAPI:
    @pytest.fixture(autouse=True)
    def setup(self):
        self.client = APIClient()
        self.user = UserFactory()
        self.car = CarFactory()

    def test_get_car_list(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.get("/api/cars/")
        assert response.status_code == status.HTTP_200_OK

        assert "count" in response.data
        assert "results" in response.data
        assert isinstance(response.data["results"], list)

        if len(response.data["results"]) > 0:
            car_data = response.data["results"][0]
            assert "id" in car_data
            assert "brand" in car_data
            assert "model" in car_data

    def test_create_car_authenticated(self):
        self.client.force_authenticate(user=self.user)
        data = {
            "brand": "Honda",
            "model": "Civic",
            "year": 2021,
            "engine_type": "petrol",
            "price": "25000.00",
            "quantity": 1,
            "dealer": self.car.dealer.id,
            "supplier": self.car.supplier.id,
        }
        response = self.client.post("/api/cars/", data, format="json")
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_create_car_unauthenticated(self):
        data = {
            "brand": "Honda",
            "model": "Civic",
            "year": 2021,
            "engine_type": "petrol",
            "price": "25000.00",
            "quantity": 1,
            "dealer": self.car.dealer.id,
            "supplier": self.car.supplier.id,
        }
        response = self.client.post("/api/cars/", data, format="json")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert "detail" in response.data
