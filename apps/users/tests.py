from django.test import TestCase
from rest_framework.reverse import reverse
from rest_framework.test import APIClient


class TestUsers(TestCase):
    def setUp(self) -> None:
        self.client = APIClient()

    def test_register(self) -> None:
        response = self.client.post(
            reverse("token_register"),
            {
                "first_name": "firstname2",
                "last_name": "lastname2",
                "email": "username2@gmail.com",
                "password": "testpwd2",
            },
        )
        self.assertEqual(response.status_code, 200)

    def test_token(self) -> None:
        self.test_register()
        response = self.client.post(
            reverse("token_obtain_pair"),
            {
                "username": "username2@gmail.com",
                "password": "testpwd2",
            },
        )
        self.assertEqual(response.status_code, 200)
