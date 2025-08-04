import pytest
from rest_framework import status
from rest_framework.test import APIClient

from autodealer_backend.users.tests.factories import UserFactory


@pytest.mark.django_db
class TestUserAPI:
    @pytest.fixture(autouse=True)
    def setup(self):
        self.client = APIClient()
        self.user = UserFactory(is_staff=True)
        self.client.force_authenticate(user=self.user)

    def test_get_user_list(self):
        UserFactory.create_batch(3)
        response = self.client.get('/api/users/')
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) == 4

    def test_create_user(self):
        data = {
            'email': 'new@example.com',
            'username': 'newuser',
            'password': 'newpass123',
            'password2': 'newpass123'
        }
        response = self.client.post('/api/users/', data)
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['email'] == data['email']

    def test_get_current_user(self):
        response = self.client.get('/api/users/me/')
        assert response.status_code == status.HTTP_200_OK
        assert response.data['email'] == self.user.email
