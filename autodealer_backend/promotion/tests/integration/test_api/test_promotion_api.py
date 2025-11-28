import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from autodealer_backend.dealers.tests.factories.dealer_factory import DealerFactory
from autodealer_backend.promotion.models.promotion_model import Promotion
from autodealer_backend.promotion.tests.factories.promotion_factory import (
    PromotionFactory,
)
from autodealer_backend.users.tests.factories.user_factory import CustomerUserFactory

User = get_user_model()


@pytest.mark.django_db
class TestPromotionAPI(APITestCase):

    def setUp(self):
        self.user = CustomerUserFactory()
        self.client.force_authenticate(user=self.user)
        self.list_url = reverse("promotion-list")
        self.dealer = DealerFactory()
        self.promotion = PromotionFactory()
        self.detail_url = reverse("promotion-detail", kwargs={"pk": self.promotion.pk})

    def test_get_promotions_list(self):
        response = self.client.get(self.list_url)
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data["results"]) >= 1

    def test_get_promotion_detail(self):
        response = self.client.get(self.detail_url)
        assert response.status_code == status.HTTP_200_OK
        assert response.data["name"] == self.promotion.name

    def test_create_promotion(self):
        data = {
            "name": "Новая акция API",
            "description": "Описание новой акции через API",
            "promotion_type": "dealer",
            "start_date": "2024-01-01T00:00:00Z",
            "end_date": "2024-12-31T23:59:59Z",
            "discount_percent": 15,
            "max_discount_amount": 50000.00,
            "dealer": self.dealer.id,
            "is_active": True,
        }

        response = self.client.post(self.list_url, data)
        assert response.status_code == status.HTTP_201_CREATED
        assert Promotion.objects.filter(name="Новая акция API").exists()

    def test_filter_promotions_by_name(self):
        PromotionFactory(name="Осенние скидки")

        response = self.client.get(self.list_url, {"name": "осенние"})
        assert response.status_code == status.HTTP_200_OK
        assert any(
            "Осенние скидки" in item["name"] for item in response.data["results"]
        )

    def test_filter_current_promotions(self):
        response = self.client.get(self.list_url, {"current": "true"})
        assert response.status_code == status.HTTP_200_OK

    def test_unauthorized_access(self):
        self.client.force_authenticate(user=None)
        response = self.client.get(self.list_url)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
