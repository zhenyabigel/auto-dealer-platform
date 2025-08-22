import pytest
from rest_framework import status
from rest_framework.test import APIClient

from autodealer_backend.users.tests.factories import UserFactory


@pytest.mark.django_db
class TestVerificationAPI:
    @pytest.fixture(autouse=True)
    def setup(self):
        self.client = APIClient()

    def test_verify_email_success(self):
        user = UserFactory(is_verified=False)
        token = user.verification_token
        data = {"token": token}
        response = self.client.post("/api/auth/verify_email/", data, format="json")
        assert response.status_code == status.HTTP_200_OK
        user.refresh_from_db()
        assert user.is_verified is True
        assert user.verification_token is None

    def test_verify_email_invalid_token(self):
        data = {"token": "invalid"}
        response = self.client.post("/api/auth/verify_email/", data, format="json")
        assert response.status_code == status.HTTP_400_BAD_REQUEST
