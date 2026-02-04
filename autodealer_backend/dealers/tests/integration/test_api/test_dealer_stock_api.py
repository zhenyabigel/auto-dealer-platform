import pytest
from rest_framework import status
from rest_framework.test import APIClient

from autodealer_backend.cars.tests.factories import CarModelFactory
from autodealer_backend.dealers.tests.factories.dealer_factory import DealerFactory
from autodealer_backend.dealers.tests.factories.dealer_stock_factory import (
    DealerStockFactory,
)
from autodealer_backend.suppliers.tests.factories.supplier_factory import (
    SupplierFactory,
)
from autodealer_backend.users.tests.factories.admin_user_factory import AdminUserFactory
from autodealer_backend.users.tests.factories.supplier_user_factory import (
    SupplierUserFactory,
)
from autodealer_backend.users.tests.factories.user_factory import UserFactory


@pytest.mark.django_db
class TestDealerStockAPI:

    @pytest.fixture(autouse=True)
    def setup(self):
        self.client = APIClient()
        self.admin = AdminUserFactory()
        self.customer = UserFactory(role="customer")

        # Создаем дилеров - фабрики сами создадут пользователей
        self.dealer = DealerFactory()
        self.other_dealer = DealerFactory()

        # Создаем поставщика
        self.supplier_user = SupplierUserFactory()
        self.supplier = SupplierFactory(user=self.supplier_user)

        self.car_model = CarModelFactory()

        # Создаем stock для основного дилера
        self.stock = DealerStockFactory(
            dealer=self.dealer,
            car_model=self.car_model,
            supplier=self.supplier,
            is_sold=False,
        )

    def test_list_stock_authenticated(self):
        self.client.force_authenticate(user=self.customer)
        response = self.client.get("/api/dealer-stock/")

        assert response.status_code == status.HTTP_200_OK
        assert "results" in response.data
        assert len(response.data["results"]) >= 1

    def test_retrieve_stock_detail(self):
        self.client.force_authenticate(user=self.customer)
        response = self.client.get(f"/api/dealer-stock/{self.stock.id}/")

        assert response.status_code == status.HTTP_200_OK
        assert response.data["id"] == self.stock.id
        assert response.data["color"] == self.stock.color
        assert "profit" in response.data
        assert "days_in_stock" in response.data

    def test_create_stock_dealer_or_admin_only(self):
        self.client.force_authenticate(user=self.customer)
        valid_data = {
            "car_model_id": self.car_model.id,
            "supplier_id": self.supplier.id,
            "purchase_price": "25000.00",
            "selling_price": "30000.00",
            "vin": "VALIDVIN123456789",
            "arrival_date": "2025-01-01",
        }
        response = self.client.post("/api/dealer-stock/", valid_data, format="json")

        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_dealer_can_create_stock_for_own_dealership(self):
        # Используем пользователя основного дилера
        self.client.force_authenticate(user=self.dealer.user)
        data = {
            "car_model_id": self.car_model.id,
            "supplier_id": self.supplier.id,
            "purchase_price": "25000.00",
            "selling_price": "30000.00",
            "vin": "NEWVIN12345678901",
            "arrival_date": "2025-01-01",
            "color": "Red",
        }
        response = self.client.post("/api/dealer-stock/", data, format="json")

        assert response.status_code == status.HTTP_201_CREATED
        assert response.data["dealer"] == self.dealer.name
        assert response.data["color"] == "Red"

    def test_admin_can_create_stock_for_any_dealer(self):
        self.client.force_authenticate(user=self.admin)
        data = {
            "dealer": self.other_dealer.id,
            "car_model_id": self.car_model.id,
            "supplier_id": self.supplier.id,
            "purchase_price": "20000.00",
            "selling_price": "25000.00",
            "vin": "ADMNCRTE123456789",
            "color": "Red",
            "arrival_date": "2025-01-01",
        }
        response = self.client.post("/api/dealer-stock/", data, format="json")

        assert response.status_code == status.HTTP_201_CREATED
        assert response.data["dealer"] == self.other_dealer.name

    def test_dealer_cannot_create_stock_for_other_dealer(self):
        self.client.force_authenticate(user=self.dealer.user)
        data = {
            "dealer": self.other_dealer.id,
            "car_model_id": self.car_model.id,
            "supplier_id": self.supplier.id,
            "purchase_price": "25000.00",
            "selling_price": "30000.00",
            "vin": "ADMNCRTE123456789",
            "arrival_date": "2025-01-01",
        }
        response = self.client.post("/api/dealer-stock/", data, format="json")

        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_create_stock_with_invalid_prices_rejected(self):
        self.client.force_authenticate(user=self.dealer.user)
        invalid_data = {
            "car_model_id": self.car_model.id,
            "supplier_id": self.supplier.id,
            "purchase_price": "30000.00",
            "selling_price": "25000.00",
            "vin": "ADMNCRTE123456789",
            "arrival_date": "2025-01-01",
        }
        response = self.client.post("/api/dealer-stock/", invalid_data, format="json")

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert any(
            "Цена продажи не может быть меньше цены покупки" in str(error)
            for error in response.data.values()
        )

    def test_invalid_vin_rejected(self):
        self.client.force_authenticate(user=self.dealer.user)
        data = {
            "car_model_id": self.car_model.id,
            "purchase_price": "20000.00",
            "selling_price": "25000.00",
            "vin": "SHORT",
            "arrival_date": "2025-01-01",
        }
        response = self.client.post("/api/dealer-stock/", data, format="json")

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "vin" in response.data

    def test_update_stock_only_by_owner_or_admin(self):
        self.client.force_authenticate(user=self.dealer.user)
        data = {"color": "Black"}
        response = self.client.patch(
            f"/api/dealer-stock/{self.stock.id}/", data, format="json"
        )

        assert response.status_code == status.HTTP_200_OK
        assert response.data["color"] == "Black"

    def test_customer_cannot_update_stock(self):
        self.client.force_authenticate(user=self.customer)
        data = {"color": "HackedColor"}
        response = self.client.patch(
            f"/api/dealer-stock/{self.stock.id}/", data, format="json"
        )

        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_other_dealer_cannot_update_stock(self):
        self.client.force_authenticate(user=self.other_dealer.user)
        data = {"color": "StolenColor"}
        response = self.client.patch(
            f"/api/dealer-stock/{self.stock.id}/", data, format="json"
        )

        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_admin_can_update_any_stock(self):
        self.client.force_authenticate(user=self.admin)
        data = {"color": "AdminUpdatedColor"}
        response = self.client.patch(
            f"/api/dealer-stock/{self.stock.id}/", data, format="json"
        )

        assert response.status_code == status.HTTP_200_OK
        assert response.data["color"] == "AdminUpdatedColor"

    def test_filter_by_dealer(self):
        other_stock = DealerStockFactory(
            dealer=self.other_dealer, car_model=self.car_model
        )

        self.client.force_authenticate(user=self.customer)
        response = self.client.get(f"/api/dealer-stock/?dealer={self.dealer.id}")

        results = response.data["results"]
        assert all(item["dealer"] == self.dealer.name for item in results)
        other_dealer_stock_ids = [
            item["id"] for item in results if item["dealer"] == self.other_dealer.name
        ]
        assert other_stock.id not in other_dealer_stock_ids

    def test_filter_by_car_model(self):
        another_model = CarModelFactory(brand="BMW", model="X5")
        DealerStockFactory(dealer=self.dealer, car_model=another_model)

        self.client.force_authenticate(user=self.customer)
        response = self.client.get(
            f"/api/dealer-stock/?car_model_id={self.car_model.id}"
        )

        results = response.data["results"]
        assert len(results) >= 1
        assert all(item["car_model"]["id"] == self.car_model.id for item in results)

    def test_sold_filter(self):
        sold_stock = DealerStockFactory(dealer=self.dealer, is_sold=True)

        self.client.force_authenticate(user=self.customer)
        response = self.client.get("/api/dealer-stock/?is_sold=False")

        assert response.status_code == status.HTTP_200_OK

        results = response.data["results"]
        ids = [item["id"] for item in results]
        assert self.stock.id in ids
        assert sold_stock.id not in ids

        response = self.client.get("/api/dealer-stock/?is_sold=True")

        assert response.status_code == status.HTTP_200_OK

        results = response.data["results"]
        ids = [item["id"] for item in results]
        assert sold_stock.id in ids
        assert self.stock.id not in ids
