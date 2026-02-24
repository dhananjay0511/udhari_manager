from django.contrib.auth.models import User
from django.test import Client, TestCase
from django.urls import reverse


class AuthTests(TestCase):
    def setUp(self):
        self.client = Client()

    def test_register_creates_user_and_logs_in(self):
        resp = self.client.post(
            reverse("accounts:register"),
            {
                "username": "newuser",
                "email": "newuser@example.com",
                "password1": "StrongPass!99",
                "password2": "StrongPass!99",
            },
        )
        self.assertRedirects(resp, "/")
        self.assertTrue(User.objects.filter(username="newuser").exists())

    def test_login_and_logout(self):
        User.objects.create_user("testuser", password="pass1234!")
        resp = self.client.post(
            reverse("accounts:login"),
            {"username": "testuser", "password": "pass1234!"},
        )
        self.assertRedirects(resp, "/")
        resp2 = self.client.post(reverse("accounts:logout"))
        self.assertRedirects(resp2, "/accounts/login/")
