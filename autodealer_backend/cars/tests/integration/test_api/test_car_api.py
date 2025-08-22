import pytest
from rest_framework import status
from rest_framework.test import APIClient

from autodealer_backend.cars.tests.factories import CarFeatureFactory, CarModelFactory
from autodealer_backend.users.tests.factories import AdminUserFactory, UserFactory


@pytest.mark.django_db
class TestCarModelAPI:
    @pytest.fixture(autouse=True)
    def setup(self):
        self.client = APIClient()
        self.user = UserFactory()
        self.admin_user = AdminUserFactory()
        self.car_model = CarModelFactory()
        self.car_feature = CarFeatureFactory(car_model=self.car_model)

    def test_get_car_model_list_authenticated(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.get("/api/cars/")
        assert response.status_code == status.HTTP_200_OK
        assert "results" in response.data
        assert isinstance(response.data["results"], list)

    def test_get_car_model_list_unauthenticated(self):
        response = self.client.get("/api/cars/models/")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_get_car_model_detail(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.get(f"/api/cars/{self.car_model.id}/")
        assert response.status_code == status.HTTP_200_OK
        assert response.data["brand"] == self.car_model.brand
        assert response.data["model"] == self.car_model.model

    def test_create_car_model_admin_only(self):
        self.client.force_authenticate(user=self.user)
        data = {
            "brand": "Tesla",
            "model": "Model S",
            "production_start": 2023,
            "engine_type": "electric",
            "engine_volume": "0.0",
            "power": 500,
            "transmission": "automatic",
            "drive_type": "awd",
            "fuel_consumption": "0.0",
            "length": 4970,
            "width": 1960,
            "height": 1440,
            "weight": 2100,
            "body_types": ["sedan"],
            "seats": 5,
            "doors": 4,
        }
        response = self.client.post("/api/cars/", data, format="json")
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_admin_can_create_car_model(self):
        self.client.force_authenticate(user=self.admin_user)
        data = {
            "brand": "Tesla",
            "model": "Model S",
            "production_start": 2023,
            "engine_type": "electric",
            "engine_volume": "0.0",
            "power": 500,
            "transmission": "automatic",
            "drive_type": "awd",
            "fuel_consumption": "0.0",
            "length": 4970,
            "width": 1960,
            "height": 1440,
            "weight": 2100,
            "body_types": ["sedan"],
            "seats": 5,
            "doors": 4,
        }
        response = self.client.post("/api/cars/", data, format="json")
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data["brand"] == "Tesla"

    def test_filter_car_models_by_brand(self):
        self.client.force_authenticate(user=self.user)
        CarModelFactory(brand="BMW")
        CarModelFactory(brand="Audi")

        response = self.client.get("/api/cars/?brand=BMW")
        assert response.status_code == status.HTTP_200_OK
        assert all(item["brand"] == "BMW" for item in response.data["results"])

    def test_car_model_features_included(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.get(f"/api/cars/{self.car_model.id}/")
        assert response.status_code == status.HTTP_200_OK
        assert "features" in response.data
        assert isinstance(response.data["features"], list)
