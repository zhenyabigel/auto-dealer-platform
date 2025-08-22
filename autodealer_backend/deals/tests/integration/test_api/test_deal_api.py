import pytest
from rest_framework.test import APIClient

from autodealer_backend.dealers.tests.factories.dealer_factory import DealerFactory
from autodealer_backend.dealers.tests.factories.dealer_stock_factory import (
    DealerStockFactory,
)
from autodealer_backend.deals.tests.factories.deals_factory import DealFactory
from autodealer_backend.suppliers.tests.factories.supplier_factory import (
    SupplierFactory,
)
from autodealer_backend.suppliers.tests.factories.supplier_offer_factory import (
    SupplierOfferFactory,
)
from autodealer_backend.users.tests.factories.user_factory import (
    AdminUserFactory,
    CustomerUserFactory,
    DealerUserFactory,
)


@pytest.mark.django_db
class TestDealAPI:
    @pytest.fixture(autouse=True)
    def setup(self):
        self.client = APIClient()
        self.customer = CustomerUserFactory()
        self.dealer_user = DealerUserFactory()
        self.supplier_user = (
            DealerUserFactory()
        )  # Создаем отдельного пользователя для поставщика
        self.admin = AdminUserFactory()

        # Создаем профили
        self.dealer = DealerFactory(user=self.dealer_user)
        self.supplier = SupplierFactory(
            user=self.supplier_user
        )  # Создаем Supplier профиль

        # Создаем автомобили для сделок
        self.dealer_stock = DealerStockFactory(dealer=self.dealer)
        self.supplier_offer = SupplierOfferFactory(
            supplier=self.supplier
        )  # Используем Supplier

        # Создаем сделки
        self.sale_deal = DealFactory(
            deal_type="sale",
            dealer_stock=self.dealer_stock,
            dealer=self.dealer_user,
            customer=self.customer,
        )
        self.purchase_deal = DealFactory(
            deal_type="purchase",
            supplier_offer=self.supplier_offer,
            dealer=self.dealer_user,
        )
