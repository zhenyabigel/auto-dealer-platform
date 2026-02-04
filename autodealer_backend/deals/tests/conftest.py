import pytest

from autodealer_backend.cars.tests.factories.car_model_factory import CarModelFactory
from autodealer_backend.dealers.tests.factories.dealer_factory import DealerFactory
from autodealer_backend.users.tests.factories.customer_user_factory import (
    CustomerUserFactory,
)


@pytest.fixture
def dealer_with_profile(db):
    """Создает дилера с профилем"""
    return DealerFactory()


@pytest.fixture
def dealer_user(db, dealer_with_profile):
    """Возвращает пользователя-дилера"""
    return dealer_with_profile.user


@pytest.fixture
def customer(db):
    """Создает покупателя"""
    return CustomerUserFactory()


@pytest.fixture
def car_model(db):
    """Создает модель автомобиля"""
    return CarModelFactory()
