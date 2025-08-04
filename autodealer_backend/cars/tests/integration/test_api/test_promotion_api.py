from datetime import timedelta

import pytest
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APIClient

from autodealer_backend.cars.tests.factories import CarFactory, PromotionFactory
from autodealer_backend.users.tests.factories import UserFactory


@pytest.mark.django_db
class TestPromotionAPI:
    @pytest.fixture(autouse=True)
    def setup(self):
        self.client = APIClient()
        self.user = UserFactory()
        self.car = CarFactory()
        self.promotion = PromotionFactory()
        self.promotion.cars.add(self.car)

    def test_get_promotion_list(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.get('/api/promotions/')
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) > 0

    def test_create_promotion(self):
        self.client.force_authenticate(user=self.user)
        data = {
            'name': 'Summer Sale',
            'description': 'Big summer discounts',
            'start_date': (timezone.now() + timedelta(days=1)).isoformat(),
            'end_date': (timezone.now() + timedelta(days=30)).isoformat(),
            'discount_percent': 20,
            'dealer': self.car.dealer.id,
            'cars': [self.car.id]
        }
        response = self.client.post('/api/promotions/', data, format='json')
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_filter_current_promotions(self):
        current_promo = PromotionFactory(
            start_date=timezone.now() - timedelta(days=1),
            end_date=timezone.now() + timedelta(days=1)
        )
        current_promo.cars.add(self.car)

        past_promo = PromotionFactory(
            start_date=timezone.now() - timedelta(days=10),
            end_date=timezone.now() - timedelta(days=5)
        )

        self.client.force_authenticate(user=self.user)
        response = self.client.get('/api/promotions/?current=true')

        assert response.status_code == status.HTTP_200_OK

        if 'results' in response.data:
            results = response.data['results']
        else:
            results = response.data

        current_ids = [p['id'] for p in results]
        assert current_promo.id in current_ids

        assert past_promo.id not in current_ids
