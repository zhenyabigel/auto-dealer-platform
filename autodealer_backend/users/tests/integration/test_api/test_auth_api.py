import pytest
from rest_framework import status
from rest_framework.test import APIClient

from autodealer_backend.users.tests.factories.user_factory import UserFactory


@pytest.mark.django_db
class TestAuthAPI:
    @pytest.fixture(autouse=True)
    def setup(self):
        self.client = APIClient()

    def test_register_user(self):
        data = {
            "email": "new@example.com",
            "username": "newuser",
            "password": "pass123",
            "password2": "pass123",
            "phone": "+1234567890",
        }
        response = self.client.post("/api/auth/register/", data, format="json")
        assert response.status_code == status.HTTP_201_CREATED
        assert User.objects.filter(email="new@example.com").exists()

    def test_login_success(self):
        user = UserFactory(password="pass123")
        data = {"email": user.email, "password": "pass123"}
        response = self.client.post("/api/auth/login/", data, format="json")
        assert response.status_code == status.HTTP_200_OK
        assert "access" in response.data
        assert "refresh" in response.data
        assert response.data["email"] == user.email

    def test_login_invalid_credentials(self):
        data = {"email": "wrong@example.com", "password": "wrong"}
        response = self.client.post("/api/auth/login/", data, format="json")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
