import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from autodealer_backend.cars.tests.factories.car_model_factory import CarModelFactory
from autodealer_backend.promotion.models.promotion_car_model import PromotionCar
from autodealer_backend.promotion.tests.factories.promotion_car_factory import (
    PromotionCarFactory,
)
from autodealer_backend.promotion.tests.factories.promotion_factory import (
    PromotionFactory,
)
from autodealer_backend.users.tests.factories.user_factory import CustomerUserFactory

User = get_user_model()


@pytest.mark.django_db
class TestPromotionCarAPI(APITestCase):

    def setUp(self):
        self.user = CustomerUserFactory()
        self.client.force_authenticate(user=self.user)
        self.list_url = reverse("promotioncar-list")
        self.promotion_car = PromotionCarFactory()
        self.detail_url = reverse(
            "promotioncar-detail", kwargs={"pk": self.promotion_car.pk}
        )

    def test_get_promotion_cars_list(self):
        response = self.client.get(self.list_url)
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data["results"]) >= 1

    def test_get_promotion_car_detail(self):
        response = self.client.get(self.detail_url)
        assert response.status_code == status.HTTP_200_OK
        assert response.data["id"] == self.promotion_car.id

    def test_create_promotion_car(self):
        promotion = PromotionFactory()
        car_model = CarModelFactory()

        data = {
            "promotion_id": promotion.id,
            "car_model_id": car_model.id,
            "special_price": 1500000.00,
        }

        response = self.client.post(self.list_url, data)
        assert response.status_code == status.HTTP_201_CREATED
        assert PromotionCar.objects.filter(
            promotion=promotion, car_model=car_model
        ).exists()

    def test_filter_by_promotion(self):
        response = self.client.get(
            self.list_url, {"promotion": self.promotion_car.promotion.id}
        )
        assert response.status_code == status.HTTP_200_OK
        assert all(
            item["promotion"] == self.promotion_car.promotion.id
            for item in response.data["results"]
        )

    def test_filter_by_car_brand(self):
        car_brand = self.promotion_car.car_model.brand
        response = self.client.get(self.list_url, {"car_brand": car_brand})
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data["results"]) >= 1

    def test_filter_active_promotions(self):
        response = self.client.get(self.list_url, {"active_promotion": "true"})
        assert response.status_code == status.HTTP_200_OK
