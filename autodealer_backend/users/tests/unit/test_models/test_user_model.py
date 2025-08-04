import pytest
from django.contrib.auth import get_user_model

User = get_user_model()


@pytest.mark.django_db
class TestUserModel:
    def test_create_user(self):
        user = User.objects.create_user(
            email="test@example.com", username="testuser", password="testpass123"
        )
        assert user.email == "test@example.com"
        assert user.check_password("testpass123")
        assert not user.is_verified
        assert user.is_active

    def test_create_superuser(self):
        admin = User.objects.create_superuser(
            email="admin@example.com", username="admin", password="adminpass123"
        )
        assert admin.is_staff
        assert admin.is_superuser

    def test_email_required(self):
        with pytest.raises(ValueError):
            User.objects.create_user(email="", username="test", password="testpass123")
