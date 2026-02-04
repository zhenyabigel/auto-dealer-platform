import pytest
from dealers.tests.factories.dealer_factory import DealerFactory

from autodealer_backend.users.tests.factories.dealer_user_factory import (
    DealerUserFactory,
)


@pytest.fixture
def dealer_user(db):
    """Создает пользователя-дилера"""
    return DealerUserFactory()


@pytest.fixture
def dealer_with_user(db):
    """Создает дилера с пользователем (корректно)"""
    user = DealerUserFactory()
    dealer = DealerFactory(user=user)
    return dealer
