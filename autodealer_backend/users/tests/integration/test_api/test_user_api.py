# users/tests/integration/test_api/test_user_api.py
import pytest
from rest_framework import status
from rest_framework.test import APIClient

from autodealer_backend.users.tests.factories import AdminUserFactory, UserFactory


@pytest.mark.django_db
class TestUserAPI:
    @pytest.fixture(autouse=True)
    def setup(self):
        self.client = APIClient()
        self.user = UserFactory()
        self.admin = AdminUserFactory()

    def test_me_endpoint_authenticated(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.get("/api/users/me/")
        assert response.status_code == status.HTTP_200_OK
        assert response.data["email"] == self.user.email

    def test_me_endpoint_unauthenticated(self):
        response = self.client.get("/api/users/me/")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_list_users_admin_only(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.get("/api/users/")
        assert response.status_code == status.HTTP_403_FORBIDDEN

        self.client.force_authenticate(user=self.admin)
        response = self.client.get("/api/users/")
        assert response.status_code == status.HTTP_200_OK
