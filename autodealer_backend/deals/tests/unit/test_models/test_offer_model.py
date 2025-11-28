from datetime import timedelta

import pytest
from django.utils import timezone

from autodealer_backend.cars.tests.factories.car_model_factory import CarModelFactory
from autodealer_backend.deals.tests.factories.offer_factory import OfferFactory
from autodealer_backend.users.tests.factories.user_factory import CustomerUserFactory


@pytest.mark.django_db
class TestOfferModel:
    def test_str_method(self):
        car_model = CarModelFactory(brand="Toyota", model="Camry")
        offer = OfferFactory(car_model=car_model)
        assert str(offer) == f"Оффер #{offer.id} ({car_model})"

    def test_is_expired_property(self):
        future_date = timezone.now() + timedelta(days=1)
        offer = OfferFactory(expiry_date=future_date)
        assert offer.is_expired is False

        past_date = timezone.now() - timedelta(days=1)
        offer = OfferFactory(expiry_date=past_date)
        assert offer.is_expired is True

    def test_save_sets_default_expiry(self):
        customer = CustomerUserFactory()
        car_model = CarModelFactory()
        offer = OfferFactory(customer=customer, car_model=car_model, expiry_date=None)
        assert offer.expiry_date is not None
        assert offer.expiry_date.date() == (timezone.now() + timedelta(days=7)).date()
