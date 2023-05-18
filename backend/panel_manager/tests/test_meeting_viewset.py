import datetime
import json

import factory
from django.db.models.signals import post_save
from django.urls import reverse
from django.utils.timezone import now
from rest_framework.response import Response
from rest_framework.test import APITestCase

from .factories import ManagerFactory, MeetingFactory, StatisticFactory, ClientFactory


@factory.django.mute_signals(post_save)
class TestMeetingViewset(APITestCase):
    def setUp(self) -> None:
        self.manager = ManagerFactory()
        self.meeting_lists = [MeetingFactory(manager=ManagerFactory()) for i in range(3)]
        self.meeting_lists.extend([MeetingFactory(manager=self.manager) for i in range(2)])
        [StatisticFactory(metting=self.meeting_lists[0], slide=f"{i}") for i in range(5)]

        self.get_statistic_detail_url = reverse(
            "panel_manager_meeting-get_statistic_detail", kwargs={"pk": self.meeting_lists[0].id}
        )
        self.list_url = reverse("panel_manager_meeting-list")
        self.specs_url = reverse("panel_manager_meeting-specs")
        self.facets_url = reverse("panel_manager_meeting-facets")
        self.upcoming_url = reverse("panel_manager_meeting-upcoming")
        self.detail_meeting_url = reverse(
            "panel_manager_meeting-detail", kwargs={"pk": self.meeting_lists[-1].id}
        )

    def test_create_meeting(self):
        """Созание встреч"""
        self.client.force_login(self.manager.user)
        client = ClientFactory()

        data = {
            "client": str(client.id),
            "manager": str(self.manager.id),
        }
        req: Response = self.client.post(self.list_url, data=data)
        req_json = req.json()
        self.assertEqual(req.status_code, 201)
        self.assertEqual(str(req_json["client"]), str(client.id))
        self.assertEqual(str(req_json["manager"]), str(self.manager.id))

    def test_list_not_auth(self):
        """Получение встреч | не авторизован"""
        req: Response = self.client.get(self.list_url)
        self.assertEqual(req.status_code, 403)
        req_json = req.json()
        self.assertEqual(req_json, {"detail": "Учетные данные не были предоставлены."})

    def test_list_auth(self):
        """Получение встреч | дефолтная сортировка по менеджеру"""

        self.client.force_login(self.manager.user)
        req: Response = self.client.get(self.list_url)
        self.assertEqual(req.status_code, 200)
        req_json = req.json()
        self.assertEqual(len(req_json), 2)

    def test_list_superuser_auth(self):
        """Получение встреч"""

        self.manager.user.is_superuser = True
        self.manager.user.save()
        self.client.force_login(self.manager.user)
        req: Response = self.client.get(self.list_url)
        self.assertEqual(req.status_code, 200)
        req_json = req.json()
        self.assertEqual(len(req_json), 5)

    def test_get_statistic(self):
        """Получение встреч"""

        self.manager.user.is_superuser = True
        self.manager.user.save()
        self.client.force_login(self.manager.user)
        req: Response = self.client.get(self.get_statistic_detail_url)
        self.assertEqual(req.status_code, 200)
        req_json = req.json()
        self.assertEqual(len(req_json["slides"]), 5)

    def test_specs(self):
        """Получение спеков"""

        self.manager.user.is_superuser = True
        self.manager.user.save()
        self.client.force_login(self.manager.user)
        req: Response = self.client.get(self.specs_url)
        self.assertEqual(req.status_code, 200)

    def test_facets(self):
        """Получение фасетов"""

        self.manager.user.is_superuser = True
        self.manager.user.save()
        self.client.force_login(self.manager.user)
        req: Response = self.client.get(self.facets_url)
        self.assertEqual(req.status_code, 200)

    def test_upcoming(self):
        """Получение предстоящих встреч"""
        [
            MeetingFactory(manager=self.manager, datetime_start=now() + datetime.timedelta(days=40))
            for i in range(2)
        ]

        self.manager.user.is_superuser = True
        self.manager.user.save()
        self.client.force_login(self.manager.user)
        req: Response = self.client.get(self.upcoming_url)
        self.assertEqual(req.status_code, 200)
        req_json = req.json()
        self.assertEqual(len(req_json), 2)

    def test_update_meeting(self):
        """Обновление встречи"""

        data = {
            "datetime_start": "2021-08-01T13:52:03.037Z",
            "datetime_end": "2021-08-01T13:52:03.037Z",
            "comment": "string",
            "purchase_purpose": 0,
            "ad_question": "string",
            "stage_solution_question": "13",
            "agreed": "string",
            "adult_count": 5,
            "child_count": 20,
            "child_len": [0, 1, 2],
            "money": 0,
            "area": {"lower": 3, "upper": 30},
            "floor": {"lower": 3, "upper": 30},
            "form_pay": 0,
            "rooms": [1, 2],
            "another_type": [0],
        }
        data_json = json.dumps(data)
        self.client.force_login(self.manager.user)
        req: Response = self.client.patch(
            self.detail_meeting_url, data=data_json, content_type="application/json"
        )
        req_json = req.json()
        self.assertEqual(req.status_code, 200)
        self.assertEqual(req_json["child_len"], data["child_len"])
        self.assertEqual(req_json["rooms"], data["rooms"])
        self.assertEqual(req_json["floor"], data["floor"])
