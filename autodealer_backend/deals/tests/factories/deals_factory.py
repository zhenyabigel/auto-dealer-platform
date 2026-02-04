from decimal import Decimal

import factory
from faker import Faker

from autodealer_backend.dealers.tests.factories.dealer_stock_factory import (
    DealerStockFactory,
)
from autodealer_backend.deals.models.deal_model import Deal
from autodealer_backend.deals.tests.factories.offer_factory import OfferFactory
from autodealer_backend.suppliers.tests.factories.supplier_offer_factory import (
    SupplierOfferFactory,
)
from autodealer_backend.users.tests.factories.customer_user_factory import (
    CustomerUserFactory,
)
from autodealer_backend.users.tests.factories.dealer_user_factory import (
    DealerUserFactory,
)

fake = Faker()


class DealFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Deal
        skip_postgeneration_save = True

    # Базовые поля, которые всегда нужны
    price = factory.LazyFunction(
        lambda: Decimal(
            str(fake.pydecimal(left_digits=6, right_digits=2, positive=True))
        )
    )
    quantity = 1
    is_completed = False
    notes = factory.LazyFunction(lambda: fake.sentence())

    # Используем итератор для автоматического выбора типа
    deal_type = factory.Iterator(["purchase", "sale"])

    @classmethod
    def _create(cls, model_class, *args, **kwargs):
        # Автоматически устанавливаем обязательные поля в зависимости от типа сделки
        deal_type = kwargs.get("deal_type", "sale")

        if deal_type == "sale":
            # Для продажи клиенту
            if "customer" not in kwargs:
                kwargs["customer"] = CustomerUserFactory()
            if "dealer_stock" not in kwargs:
                kwargs["dealer_stock"] = DealerStockFactory()
            if "offer" not in kwargs:
                kwargs["offer"] = OfferFactory(customer=kwargs["customer"])
            # НЕ УБИРАЕМ dealer, если он передан!
            # kwargs.pop("dealer", None)  # УБРАТЬ ЭТУ СТРОКУ!
            # Также не убираем supplier_offer, он может быть null
            kwargs.pop("supplier_offer", None)
        else:  # purchase
            # Для покупки у поставщика
            if "dealer" not in kwargs:
                kwargs["dealer"] = DealerUserFactory()
            if "supplier_offer" not in kwargs:
                kwargs["supplier_offer"] = SupplierOfferFactory()
            # НЕ УБИРАЕМ customer и dealer_stock, если они переданы
            # kwargs.pop("customer", None)  # УБРАТЬ!
            # kwargs.pop("dealer_stock", None)  # УБРАТЬ!
            # kwargs.pop("offer", None)  # УБРАТЬ!

        return super()._create(model_class, *args, **kwargs)
