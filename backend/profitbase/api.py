from datetime import timedelta
from typing import List

import requests
from django.conf import settings
from django.utils import timezone
from django.utils.timezone import now
from requests import HTTPError
from rest_framework_tracking.models import APIRequestLog
from retry import retry

from profitbase import logger


class ProfitBaseAPI(object):
    """
    API profitbase
    """

    def __init__(self, access_token: str = None):
        self.api_key = settings.PROFITBASE_API_KEY
        self.base_url = settings.PROFITBASE_BASE_URL
        self.access_token = access_token if access_token else None
        self.expire_time = None
        self.floors_count_data = {}
        self.authenticate()

    def authenticate(self):
        data = {"type": "api-app", "credentials": {"pb_api_key": self.api_key}}
        response = requests.post(f"{self.base_url}/authentication", json=data)
        response.raise_for_status()
        json = response.json()
        if "access_token" in json:
            self.access_token = json["access_token"]
            self.expire_time = timezone.now() + timedelta(seconds=json["remaining_time"])
        return True

    def request(self, method, path, params=None, data=None, logs: bool = False):
        if self.expire_time < timezone.now():
            self.authenticate()
        if not path.startswith("/"):
            path = f"/{path}"
        url = f"{self.base_url}{path}"
        if not params:
            params = {}
        params.update({"access_token": self.access_token})
        response = None
        if method == "GET":
            response = requests.get(url, params=params, json=data)
            if response.status_code in (401, 403):
                self.authenticate()
                params.update({"access_token": self.access_token})
                response = requests.get(url, params=params, json=data)
        elif method == "POST":
            response = requests.post(url, params=params, json=data)
            if response.status_code in (401, 403):
                self.authenticate()
                params.update({"access_token": self.access_token})
                response = requests.post(url, params=params, json=data)

        if logs:
            try:
                APIRequestLog.objects.create(
                    requested_at=now(),
                    path=url,
                    view="url",
                    view_method=path,
                    remote_addr="0.0.0.0",
                    host="https://localhost",
                    method=method,
                    data="none",
                    response=str(response.text),
                    status_code=response.status_code,
                )
            except Exception as e:
                logger.exception("Error logging API request")
        response.raise_for_status()
        if response:
            return response.json()
        raise NotImplementedError(f"method {method} is not allowed")

    def get(self, url, params=None, data=None):
        return self.request("GET", url, params, data)

    def post(self, url, params=None, data=None, logs: bool = False):
        return self.request("POST", url, params, data, logs)

    def get_projects(self):
        return self.get("/projects")

    def get_houses(self, house_id: int = None):
        params = {"id": house_id} if house_id else {}
        response = self.get(f"/house", params=params)
        if response["success"]:
            return response["data"]
        return None

    def get_special_offers(self):
        return self.get("/special-offer")

    @retry((HTTPError, requests.RequestException), delay=1, backoff=2, logger=logger)
    def _get_property(self, params: dict, auth_attempts=0):
        try:
            response = self.get("/property",params=params)
        except requests.ConnectionError as e:
            raise e
        except (requests.RequestException, HTTPError) as e:
            if e.response.status_code == 403 and auth_attempts < 10:
                self.authenticate()
                auth_attempts += 1
            raise e
        return response, auth_attempts

    def get_properties(self, project_id: str):
        """
        Генератор
        """
        limit = 50
        offset = 0
        has_next = True
        auth_attempts = 0
        while has_next:
            response, auth_attempts = self._get_property(
                {
                    "full": "true",
                    "projectId": project_id,
                    "limit": limit,
                    "offset": offset,
                }, auth_attempts
            )
            if response and response["status"] == "success":
                yield from response["data"]
            has_next = len(response["data"]) == limit
            offset += limit

    def get_property_types(self):
        return self.get("/property-types")

    def property_booking(self, id_property: str, deal_id: str):
        """Бронирование помещения в Profitbase"""
        self.post(
            "/crm/addPropertyDeal", data=dict(propertyId=id_property, dealId=deal_id), logs=True
        )

    def property_unbooking(self, deal_id: str):
        """Разбронирование помещения в Profitbase"""
        self.post("/crm/removePropertyDeal", data=dict(dealId=deal_id), logs=True)

    def get_floors_count(self, building_id: int) -> List[dict]:
        """Получение данных об этажности здания.

        Returns:
            list: список словарей с ключами section_id, title, count, above-ground, underground
        """
        if building_id in self.floors_count_data.keys():
            return self.floors_count_data[building_id]
        response = self.get("/house/get-count-floors", params={"houseId": building_id})
        if "data" not in response.keys() or not isinstance(response["data"], list):
            logger.error(f"Profitbase вернул неожиданный ответ: {response}")
            return []
        self.floors_count_data[building_id] = response["data"]
        return response["data"]
