import pytest
from rest_framework import status
from rest_framework.test import APIClient

from autodealer_backend.cars.tests.factories import CarFeatureFactory, CarModelFactory
from autodealer_backend.users.tests.factories import UserFactory


@pytest.mark.django_db
class TestCarFeatureAPI:
    @pytest.fixture(autouse=True)
    def setup(self):
        self.client = APIClient()
        self.user = UserFactory()
        self.admin_user = UserFactory(is_staff=True, is_superuser=True)
        self.car_model = CarModelFactory()
        self.car_feature = CarFeatureFactory(car_model=self.car_model)

    def test_get_car_features_list_admin_only(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.get("/api/cars-feature/")
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_admin_can_get_car_features_list(self):
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.get("/api/cars-feature/")
        assert response.status_code == status.HTTP_200_OK
        assert "results" in response.data

    def test_filter_features_by_category(self):
        self.client.force_authenticate(user=self.admin_user)
        CarFeatureFactory(car_model=self.car_model, category="safety")
        CarFeatureFactory(car_model=self.car_model, category="comfort")

        response = self.client.get("/api/cars-feature/?category=safety")
        assert response.status_code == status.HTTP_200_OK
        assert all(item["category"] == "safety" for item in response.data["results"])
