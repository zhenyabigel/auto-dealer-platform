from datetime import timedelta

import pytest
from django.utils import timezone

from autodealer_backend.promotion.serializers import PromotionSerializer
from autodealer_backend.promotion.tests.factories.promotion_factory import (
    DealerFactory,
    PromotionFactory,
)


@pytest.mark.django_db
class TestPromotionSerializer:

    def test_serializer_with_valid_data(self):
        promotion = PromotionFactory()
        serializer = PromotionSerializer(promotion)

        data = serializer.data
        assert data["id"] == promotion.id
        assert data["name"] == promotion.name
        assert data["promotion_type"] == promotion.promotion_type
        assert "promotion_type_display" in data
        assert "dealer_name" in data
        assert "is_active_now" in data

    def test_serializer_validation_valid(self):
        dealer = DealerFactory()
        data = {
            "name": "Тестовая акция",
            "description": "Описание тестовой акции",
            "promotion_type": "dealer",
            "start_date": timezone.now() + timedelta(days=1),
            "end_date": timezone.now() + timedelta(days=10),
            "discount_percent": 15,
            "max_discount_amount": 50000.00,
            "dealer": dealer.id,
            "is_active": True,
        }

        serializer = PromotionSerializer(data=data)
        assert serializer.is_valid()

    def test_serializer_validation_dealer_required(self):
        data = {
            "name": "Тестовая акция",
            "description": "Описание тестовой акции",
            "promotion_type": "dealer",
            "start_date": timezone.now() + timedelta(days=1),
            "end_date": timezone.now() + timedelta(days=10),
            "discount_percent": 15,
            "is_active": True,
        }

        serializer = PromotionSerializer(data=data)
        assert not serializer.is_valid()
        assert "non_field_errors" in serializer.errors

    def test_serializer_validation_dates(self):
        data = {
            "name": "Тестовая акция",
            "description": "Описание тестовой акции",
            "promotion_type": "supplier",
            "start_date": timezone.now() + timedelta(days=10),
            "end_date": timezone.now() + timedelta(days=1),
            "discount_percent": 15,
            "is_active": True,
        }

        serializer = PromotionSerializer(data=data)
        assert not serializer.is_valid()
        assert "non_field_errors" in serializer.errors

    def test_supplier_promotion_no_dealer_validation(self):
        data = {
            "name": "Тестовая акция поставщика",
            "description": "Описание",
            "promotion_type": "supplier",
            "start_date": timezone.now() + timedelta(days=1),
            "end_date": timezone.now() + timedelta(days=10),
            "discount_percent": 10,
            "is_active": True,
        }

        serializer = PromotionSerializer(data=data)
        assert serializer.is_valid()
