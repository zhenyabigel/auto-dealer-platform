import pytest
from rest_framework import status
from rest_framework.test import APIClient

from autodealer_backend.cars.tests.factories import CarModelFactory
from autodealer_backend.dealers.tests.factories.dealer_factory import DealerFactory
from autodealer_backend.users.tests.factories.admin_user_factory import AdminUserFactory
from autodealer_backend.users.tests.factories.user_factory import UserFactory


@pytest.mark.django_db
class TestDealerAPI:
    @pytest.fixture(autouse=True)
    def setup(self):
        self.client = APIClient()
        self.admin = AdminUserFactory()
        self.dealer = DealerFactory()
        self.customer = UserFactory(role="customer")
        self.car_model = CarModelFactory()
        self.dealer.preferred_car_models.add(self.car_model)

    def test_list_dealers_authenticated(self):
        self.client.force_authenticate(user=self.admin)
        response = self.client.get("/api/dealers/")
        assert response.status_code == status.HTTP_200_OK
        assert "results" in response.data
        assert len(response.data["results"]) >= 1

    def test_list_dealers_unauthenticated(self):
        response = self.client.get("/api/dealers/")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_retrieve_dealer_detail(self):
        self.client.force_authenticate(user=self.customer)
        response = self.client.get(f"/api/dealers/{self.dealer.id}/")
        assert response.status_code == status.HTTP_200_OK
        assert response.data["name"] == self.dealer.name
        assert "preferred_car_models" in response.data
        assert len(response.data["preferred_car_models"]) == 1

    def test_non_admin_cannot_create_dealer(self):
        self.client.force_authenticate(user=self.customer)
        data = {"name": "Hacker Dealer", "location": "US", "phone": "+1"}
        response = self.client.post("/api/dealers/", data, format="json")
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_admin_can_create_dealer(self):
        self.client.force_authenticate(user=self.admin)

        # Создаем нового пользователя для дилера
        from autodealer_backend.users.tests.factories.dealer_user_factory import (
            DealerUserFactory,
        )

        user = DealerUserFactory()  # Создаем пользователя с role="dealer"

        data = {
            "user": user.id,
            "name": "Premium Motors",
            "location": "US",
            "phone": "+1234567890",
            "balance": "50000.00",
        }
        response = self.client.post("/api/dealers/", data, format="json")
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data["name"] == "Premium Motors"
        assert response.data["user"] == user.id

    def test_admin_can_update_any_dealer(self):
        self.client.force_authenticate(user=self.admin)
        data = {"name": "Admin Updated Name"}
        response = self.client.patch(
            f"/api/dealers/{self.dealer.id}/", data, format="json"
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.data["name"] == "Admin Updated Name"

    def test_update_dealer_by_owner_or_admin(self):
        # Используем пользователя дилера, а не создаем нового
        self.client.force_authenticate(user=self.dealer.user)
        data = {"name": "Updated Name", "phone": "+9876543210"}
        response = self.client.patch(
            f"/api/dealers/{self.dealer.id}/", data, format="json"
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.data["name"] == "Updated Name"

    def test_customer_cannot_update_dealer(self):
        self.client.force_authenticate(user=self.customer)
        data = {"name": "Hacked"}
        response = self.client.patch(f"/api/dealers/{self.dealer.id}/", data)
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_filter_dealers_by_location(self):
        # Создаем новых дилеров для фильтрации
        moscow_dealer = DealerFactory(name="Moscow Dealer", location="RU")
        berlin_dealer = DealerFactory(name="Berlin Dealer", location="DE")

        self.client.force_authenticate(user=self.customer)
        response = self.client.get("/api/dealers/?location=RU")
        assert response.status_code == status.HTTP_200_OK
        names = [item["name"] for item in response.data["results"]]
        assert "Moscow Dealer" in names
        assert "Berlin Dealer" not in names

    def test_search_dealers_by_name(self):
        # Создаем новых дилеров для поиска
        DealerFactory(name="Luxury Auto Center")
        DealerFactory(name="Budget Cars")

        self.client.force_authenticate(user=self.customer)
        response = self.client.get("/api/dealers/?search=Luxury")
        assert response.status_code == status.HTTP_200_OK
        assert any("Luxury" in item["name"] for item in response.data["results"])
