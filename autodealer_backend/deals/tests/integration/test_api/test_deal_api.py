from decimal import Decimal

import pytest
from rest_framework import status
from rest_framework.test import APIClient
from users.tests.factories.user_factory import UserFactory

from autodealer_backend.cars.tests.factories import CarModelFactory
from autodealer_backend.dealers.tests.factories.dealer_factory import DealerFactory
from autodealer_backend.dealers.tests.factories.dealer_stock_factory import (
    DealerStockFactory,
)
from autodealer_backend.deals.models.deal_model import Deal
from autodealer_backend.deals.tests.factories.deals_factory import DealFactory
from autodealer_backend.deals.tests.factories.offer_factory import OfferFactory
from autodealer_backend.suppliers.tests.factories.supplier_factory import (
    SupplierFactory,
)
from autodealer_backend.suppliers.tests.factories.supplier_offer_factory import (
    SupplierOfferFactory,
)


@pytest.mark.django_db
class TestDealAPI:
    @pytest.fixture(autouse=True)
    def setup(self):
        self.client = APIClient()
        self.admin = UserFactory(is_staff=True, is_superuser=True)
        self.dealer_user = UserFactory(role="dealer")
        self.customer = UserFactory(role="customer")
        self.another_customer = UserFactory(role="customer")

        self.dealer = DealerFactory(user=self.dealer_user)
        self.car_model = CarModelFactory()
        self.supplier = SupplierFactory()
        self.dealer_stock = DealerStockFactory(
            dealer=self.dealer, car_model=self.car_model
        )
        self.supplier_offer = SupplierOfferFactory(supplier=self.supplier)

        self.offer = OfferFactory(
            customer=self.customer,
            car_model=self.car_model,
            max_price=Decimal("30000.00"),
        )

        self.sale_deal = DealFactory(
            deal_type="sale",
            customer=self.customer,
            dealer_stock=self.dealer_stock,
            price=Decimal("25000.00"),
            quantity=1,
            is_completed=True,
        )

        self.purchase_deal = DealFactory(
            deal_type="purchase",
            dealer=self.dealer_user,
            supplier_offer=self.supplier_offer,
            price=Decimal("20000.00"),
            quantity=1,
            is_completed=False,
        )

    def test_deals_created_in_db(self):
        assert Deal.objects.count() >= 2
        assert self.sale_deal.id is not None
        assert self.purchase_deal.id is not None

    def test_list_deals_authenticated_dealer(self):
        self.client.force_authenticate(user=self.dealer_user)
        response = self.client.get("/api/deals/")
        assert response.status_code == status.HTTP_200_OK
        deals = response.data["results"]
        dealer_deals = [
            deal for deal in deals if deal.get("dealer") == self.dealer_user.id
        ]
        assert len(dealer_deals) >= 1

    def test_list_deals_authenticated_customer(self):
        self.client.force_authenticate(user=self.customer)
        response = self.client.get("/api/deals/")
        assert response.status_code == status.HTTP_200_OK
        deals = response.data["results"]
        customer_deals = [
            deal for deal in deals if deal.get("customer") == self.customer.id
        ]
        assert len(customer_deals) >= 1

    def test_list_deals_unauthenticated(self):
        response = self.client.get("/api/deals/")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_retrieve_own_deal_customer(self):
        self.client.force_authenticate(user=self.customer)
        response = self.client.get(f"/api/deals/{self.sale_deal.id}/")
        assert response.status_code == status.HTTP_200_OK
        assert response.data["customer"] == self.customer.id

    def test_retrieve_others_deal_customer(self):
        self.client.force_authenticate(user=self.another_customer)
        response = self.client.get(f"/api/deals/{self.sale_deal.id}/")
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_retrieve_purchase_deal_dealer(self):
        self.client.force_authenticate(user=self.dealer_user)
        response = self.client.get(f"/api/deals/{self.purchase_deal.id}/")
        assert response.status_code == status.HTTP_200_OK
        assert response.data["dealer"] == self.dealer_user.id
        assert response.data["deal_type"] == "purchase"

    def test_create_sale_deal_admin(self):
        self.client.force_authenticate(user=self.admin)
        data = {
            "deal_type": "sale",
            "customer": self.customer.id,
            "dealer_stock": self.dealer_stock.id,
            "price": "27000.00",
            "quantity": 1,
            "is_completed": False,
            "notes": "Test sale deal",
        }
        response = self.client.post("/api/deals/", data, format="json")
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data["deal_type"] == "sale"
        assert Decimal(response.data["price"]) == Decimal("27000.00")

    def test_create_purchase_deal_dealer(self):
        self.client.force_authenticate(user=self.dealer_user)
        data = {
            "deal_type": "purchase",
            "supplier_offer": self.supplier_offer.id,
            "price": "22000.00",
            "quantity": 1,
            "is_completed": False,
            "notes": "Test purchase from supplier",
        }
        response = self.client.post("/api/deals/", data, format="json")
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data["deal_type"] == "purchase"

    def test_filter_deals_by_type(self):
        self.client.force_authenticate(user=self.admin)
        response = self.client.get("/api/deals/?deal_type=sale")
        assert response.status_code == status.HTTP_200_OK
        deals = response.data["results"]
        assert all(deal["deal_type"] == "sale" for deal in deals)

    def test_filter_deals_by_completion_status(self):
        self.client.force_authenticate(user=self.admin)
        response = self.client.get("/api/deals/?completed=true")
        assert response.status_code == status.HTTP_200_OK
        deals = response.data["results"]
        assert all(deal["is_completed"] is True for deal in deals)

    def test_complete_deal_action_dealer(self):
        self.client.force_authenticate(user=self.dealer_user)
        response = self.client.post(f"/api/deals/{self.purchase_deal.id}/complete/")
        assert response.status_code == status.HTTP_200_OK

    def test_complete_others_deal_customer(self):
        self.client.force_authenticate(user=self.another_customer)
        response = self.client.post(f"/api/deals/{self.sale_deal.id}/complete/")
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_create_deal_invalid_price(self):
        self.client.force_authenticate(user=self.admin)
        data = {
            "deal_type": "sale",
            "customer": self.customer.id,
            "dealer_stock": self.dealer_stock.id,
            "price": "-100.00",
            "quantity": 1,
        }
        response = self.client.post("/api/deals/", data, format="json")
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "price" in response.data
