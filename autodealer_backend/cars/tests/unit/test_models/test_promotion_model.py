from datetime import timedelta

import pytest
from django.utils import timezone

from autodealer_backend.cars.tests.factories import PromotionFactory


@pytest.mark.django_db
class TestPromotionModel:
    @pytest.fixture
    def promotion(self):
        return PromotionFactory()

    def test_promotion_creation(self, promotion):
        assert promotion.name is not None
        assert timezone.now() - timedelta(days=2) <= promotion.start_date <= timezone.now()
        assert promotion.start_date < promotion.end_date
        assert 1 <= promotion.discount_percent <= 100
        assert promotion.is_active is True
