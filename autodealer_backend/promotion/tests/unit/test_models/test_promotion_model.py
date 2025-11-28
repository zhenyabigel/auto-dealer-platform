from datetime import timedelta

import pytest
from django.utils import timezone

from autodealer_backend.promotion.models.promotion_model import Promotion
from autodealer_backend.promotion.tests.factories.promotion_factory import (
    DealerFactory,
    PromotionFactory,
)


@pytest.mark.django_db
class TestPromotionModel:

    def test_promotion_creation(self):
        promotion = PromotionFactory()
        assert promotion.name is not None
        assert promotion.description is not None
        assert promotion.promotion_type in ["supplier", "dealer"]
        assert promotion.start_date < promotion.end_date
        assert promotion.is_active is True

    def test_promotion_str(self):
        promotion = PromotionFactory(name="Летняя распродажа")
        assert str(promotion) == "Летняя распродажа"

    def test_supplier_promotion_no_dealer(self):
        promotion = PromotionFactory(promotion_type="supplier", dealer=None)
        assert promotion.promotion_type == "supplier"
        assert promotion.dealer is None

    def test_dealer_promotion_requires_dealer(self):
        dealer = DealerFactory()
        promotion = PromotionFactory(promotion_type="dealer", dealer=dealer)
        assert promotion.promotion_type == "dealer"
        assert promotion.dealer == dealer

    def test_is_active_now_property(self):
        promotion = PromotionFactory(
            start_date=timezone.now() - timedelta(days=1),
            end_date=timezone.now() + timedelta(days=1),
            is_active=True,
        )
        assert promotion.is_active_now is True

        promotion = PromotionFactory(
            start_date=timezone.now() + timedelta(days=1),
            end_date=timezone.now() + timedelta(days=2),
            is_active=True,
        )
        assert promotion.is_active_now is False

        promotion = PromotionFactory(
            start_date=timezone.now() - timedelta(days=1),
            end_date=timezone.now() + timedelta(days=1),
            is_active=False,
        )
        assert promotion.is_active_now is False

    def test_promotion_type_display(self):
        promotion = PromotionFactory(promotion_type="supplier")
        assert promotion.get_promotion_type_display() == "От поставщика"

        promotion = PromotionFactory(promotion_type="dealer")
        assert promotion.get_promotion_type_display() == "От дилера"

    def test_meta_ordering(self):
        promotion1 = PromotionFactory(start_date=timezone.now() - timedelta(days=2))
        promotion2 = PromotionFactory(start_date=timezone.now() - timedelta(days=1))

        promotions = Promotion.objects.all()
        assert promotions[0] == promotion2
        assert promotions[1] == promotion1
