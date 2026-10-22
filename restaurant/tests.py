
from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework.authtoken.models import Token

from .models import Menu


class MenuAPITests(APITestCase):
    def setUp(self):
        self.customer = User.objects.create_user(
            username="testcustomer",
            password="TestPassword123!",
        )
        self.manager = User.objects.create_user(
            username="testmanager",
            password="TestPassword123!",
        )

        from django.contrib.auth.models import Group
        manager_group, _ = Group.objects.get_or_create(name="Manager")
        self.manager.groups.add(manager_group)

        self.menu = Menu.objects.create(
            title="Greek Salad",
            price="12.50",
            inventory=20,
        )

    def test_menu_list_is_public(self):
        response = self.client.get("/api/menu-items")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_anonymous_user_cannot_create_menu_item(self):
        response = self.client.post(
            "/api/menu-items",
            {
                "title": "Bruschetta",
                "price": "8.50",
                "inventory": 10,
            },
            format="json",
        )
        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED,
        )

    def test_manager_can_create_menu_item(self):
        token = Token.objects.create(user=self.manager)
        self.client.credentials(
            HTTP_AUTHORIZATION=f"Token {token.key}"
        )

        response = self.client.post(
            "/api/menu-items",
            {
                "title": "Bruschetta",
                "price": "8.50",
                "inventory": 10,
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
        )
