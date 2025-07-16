import pytest
from rest_framework import status
from rest_framework.test import APIClient

from autodealer_backend.users.tests.factories import UserFactory


@pytest.mark.django_db
class TestAuthAPI:
    @pytest.fixture(autouse=True)
    def setup(self):
        self.client = APIClient()
        self.user = UserFactory(password='testpass123')

    def test_login_success(self):
        self.user.is_active = True
        self.user.is_verified = True
        self.user.save()

        data = {
            'email': self.user.email,
            'password': 'testpass123'
        }
        response = self.client.post('/api/auth/login/', data)
        assert response.status_code == status.HTTP_200_OK
        assert 'access' in response.data

    def test_login_invalid_credentials(self):
        data = {
            'email': self.user.email,
            'password': 'wrongpassword'
        }
        response = self.client.post('/api/auth/login/', data)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
