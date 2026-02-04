from users.tests.factories.user_factory import UserFactory


class CustomerUserFactory(UserFactory):
    role = "customer"
