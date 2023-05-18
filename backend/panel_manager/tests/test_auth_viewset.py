import factory
from django.db.models.signals import post_save
from django.urls import reverse
from rest_framework.response import Response
from rest_framework.test import APITestCase

from panel_manager.tests.factories import ManagerFactory


@factory.django.mute_signals(post_save)
class TestAuthManagerViewset(APITestCase):
    def setUp(self) -> None:
        self.list_url = reverse("panel_manager_auth-list")
        self.login_url = reverse("panel_manager_auth-login")
        self.logout_url = reverse("panel_manager_auth-logout")
        self.manager = ManagerFactory()
        self.login_data = {"username": "string", "password": "string"}

    def test_list_not_auth(self):
        """Получение информации пользователя | не авторизован"""
        req: Response = self.client.get(self.list_url)
        self.assertEqual(req.status_code, 404)

    def test_list_auth(self):
        """Получение информации пользователя"""

        self.client.force_login(self.manager.user)
        req: Response = self.client.get(self.list_url)
        self.assertEqual(req.status_code, 200)
        req_json = req.json()
        self.assertEqual(req_json["id"], self.manager.user.id)

    def test_login_not_found(self):
        """Авторизация менеджера | не найдет"""

        req: Response = self.client.post(self.login_url, data=self.login_data)
        self.assertEqual(req.status_code, 400)

    def test_login(self):
        """Авторизация менеджера | не найдет"""
        self.login_data["username"] = self.manager.login
        req: Response = self.client.post(self.login_url, data=self.login_data)
        self.assertEqual(req.status_code, 200)
        req_json = req.json()
        self.assertEqual(req_json["id"], self.manager.user.id)
        req: Response = self.client.get(self.list_url)
        self.assertEqual(req.status_code, 200)
        req_json = req.json()
        self.assertEqual(req_json["id"], self.manager.user.id)

    def test_logout(self):
        """Выход вон!"""

        self.client.force_login(self.manager.user)
        req: Response = self.client.post(self.logout_url, data={})
        self.assertEqual(req.status_code, 200)
        req: Response = self.client.get(self.list_url)
        self.assertEqual(req.status_code, 404)
