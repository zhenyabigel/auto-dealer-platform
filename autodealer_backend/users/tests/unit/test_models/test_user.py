import pytest

from autodealer_backend.users.models import User
from autodealer_backend.users.tests.factories import CustomerUserFactory, UserFactory


@pytest.mark.django_db
class TestUserModel:
    def test_str_method(self):
        user = UserFactory(email="test@example.com", role="customer")
        assert str(user) == "test@example.com (Покупатель)"

    def test_create_user_with_email(self):
        user = User.objects.create_user(email="user@example.com", password="pass")
        assert user.email == "user@example.com"
        assert user.username == "user@example.com"
        assert not user.is_staff
        assert not user.is_superuser

    def test_create_superuser(self):
        admin = User.objects.create_superuser(
            email="admin@example.com", password="pass"
        )
        assert admin.is_staff
        assert admin.is_superuser
        assert admin.role == "admin"

    def test_email_required(self):
        with pytest.raises(ValueError, match="Email is required"):
            User.objects.create_user(email="")

    def test_unique_email_constraint(self):
        UserFactory(email="unique@example.com")
        with pytest.raises(Exception):
            UserFactory(email="unique@example.com")

    def test_verification_token_generated(self):
        user = UserFactory(is_verified=False, verification_token=None)
        assert user.verification_token is not None
        assert len(user.verification_token) == 64

    def test_no_verification_token_if_verified(self):
        user = UserFactory(is_verified=True, verification_token=None)
        assert user.verification_token is None

    def test_properties(self):
        customer = CustomerUserFactory()
        assert customer.is_customer is True
        assert customer.is_dealer is False
        assert customer.is_supplier is False
