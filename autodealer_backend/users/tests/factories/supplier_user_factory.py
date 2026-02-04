from users.tests.factories.user_factory import UserFactory


class SupplierUserFactory(UserFactory):
    role = "supplier"
