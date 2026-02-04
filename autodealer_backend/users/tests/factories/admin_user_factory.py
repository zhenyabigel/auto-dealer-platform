from users.tests.factories.user_factory import UserFactory


class AdminUserFactory(UserFactory):
    role = "admin"
    is_staff = True
    is_superuser = True
