from logging import getLogger

import requests
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.utils.timezone import now
from rest_framework_tracking.models import APIRequestLog

from properties.constants import PropertyType

from .models import AmoCRMSettings
from .tasks import create_note, create_task, update_lead

logger = getLogger(__name__)


class AmoCRM:
    CRM_URL = "https://eurobereg72.amocrm.ru/"
    API_URL = CRM_URL + "api/v2/"
    API_V4_URL = CRM_URL + "api/v4/"
    AUTH_URL = CRM_URL + "oauth2/access_token/"
    req = requests.Session()
    PHONE_FIELD_ID = 362093
    PHONE_FIELD_ENUM = 706657
    PROP_TYPE_FIELD_ID = 366965
    PROP_TYPE_FIELD_VALUES = {
        PropertyType.FLAT: {"enum": 715523, "value": "Квартира"},
        PropertyType.COMMERCIAL_APARTMENT: {"enum": 1324118, "value": "Апартаменты"},
        PropertyType.PARKING: {"enum": 715525, "value": "Паркинг"},
        PropertyType.COMMERCIAL: {"enum": 1311059, "value": "Коммерция"},
    }
    EMAIL_ID = 362095
    PROJ_FIELD_ID = 596489
    DESC_FIELD_ID = 547667
    ROISTAT_ID = 640801
    SMART_VISITOR_ID = 693854
    SMART_SESSION_ID = 693806
    METRIKA_CID = 694350
    GOOGLE_CID = 640853
    UTM_SOURCE = 640865
    UTM_MEDIUM = 640867
    UTM_CONTENT = 640871
    UTM_CAMPAIGN = 640877
    UTM_TERM = 640873
    URL_FIELD_ID = 822858
    CITY_NAME_ID = 692726
    CITY_NAME_VALUES = {
        "ТМН": {"enum": 1322598, "value": "Тюмень"},
        "МСК": {"enum": 1322604, "value": "Москва"},
        "СПБ": {"enum": 1322602, "value": "Санкт-Петербург"},
        "ЕКБ": {"enum": 1322600, "value": "Екатеринбург"},
    }

    @staticmethod
    def get_config():
        config = AmoCRMSettings.get_solo()
        if not config.is_valid():
            raise ImproperlyConfigured("Не заполнены ключи доступа для AmoCRM")

        return config

    def get_headers(self):
        config = self.get_config()
        return {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {config.access_token}",
        }

    def get_tags(self, old_tags=None):
        tag_names = ["Заявка с сайта", "Страна"]
        if old_tags:
            old_tag_names = [tag["name"] for tag in old_tags]
            tag_names = set(tag_names + old_tag_names)
        return ",".join(tag_names)

    def request_get(self, path):
        url = self.API_URL + path
        headers = self.get_headers()
        res = self.req.get(url, cookies=self.req.cookies, headers=headers)
        if res.status_code == 401:
            self.refresh_auth()
            headers = self.get_headers()
            res = self.req.get(url, cookies=self.req.cookies, headers=headers)

        res.raise_for_status()
        return res

    def request_post(self, path, data):
        url = self.API_URL + path

        headers = self.get_headers()
        res = self.req.post(url, json=data, cookies=self.req.cookies, headers=headers)
        if res.status_code == 401:
            self.refresh_auth()
            headers = self.get_headers()
            res = self.req.post(url, json=data, cookies=self.req.cookies, headers=headers)

        try:
            APIRequestLog.objects.create(
                requested_at=now(),
                path=url,
                view="url",
                view_method="POST",
                remote_addr="0.0.0.0",
                host="https://localhost",
                method="GET",
                data="none",
                response=str(res.text),
                status_code=res.status_code,
            )
        except Exception as e:
            logger.exception("Ошибка запроса к AmoCRM")

        res.raise_for_status()
        return res

    def request_get_v4(self, path):
        url = self.API_V4_URL + path
        headers = self.get_headers()
        res = self.req.get(url, cookies=self.req.cookies, headers=headers)
        if res.status_code == 401:
            self.refresh_auth()
            headers = self.get_headers()
            res = self.req.get(url, cookies=self.req.cookies, headers=headers)

        try:
            APIRequestLog.objects.create(
                requested_at=now(),
                path=url,
                view="url",
                view_method="GET",
                remote_addr="0.0.0.0",
                host="https://localhost",
                method="GET",
                data="none",
                response=str(res.text),
                status_code=res.status_code,
            )
        except Exception as e:
            logger.exception("Ошибка запроса к AmoCrm")
        res.raise_for_status()
        return res

    def request_patch_v4(self, path, data):
        url = self.API_V4_URL + path

        headers = self.get_headers()
        res = self.req.patch(url, json=data, cookies=self.req.cookies, headers=headers)
        if res.status_code == 401:
            self.refresh_auth()
            headers = self.get_headers()
            res = self.req.patch(url, json=data, cookies=self.req.cookies, headers=headers)
        try:
            APIRequestLog.objects.create(
                requested_at=now(),
                path=url,
                view="url",
                view_method="PATH",
                remote_addr="0.0.0.0",
                host="https://localhost",
                method="PATH",
                data=str(data),
                response=str(res.text),
                status_code=res.status_code,
            )
        except Exception as e:
            logger.exception("Ошибка запроса к AmoCrm")
        res.raise_for_status()
        return res

    def request_post_v4(self, path, data):
        url = self.API_V4_URL + path

        headers = self.get_headers()
        res = self.req.post(url, json=data, cookies=self.req.cookies, headers=headers)
        if res.status_code == 401:
            self.refresh_auth()
            headers = self.get_headers()
            res = self.req.post(url, json=data, cookies=self.req.cookies, headers=headers)
        try:
            APIRequestLog.objects.create(
                requested_at=now(),
                path=url,
                view="url",
                view_method="POST",
                remote_addr="0.0.0.0",
                host="https://localhost",
                method="POST",
                data=str(data),
                response=str(res.text),
                status_code=res.status_code,
            )
        except Exception as e:
            logger.exception("Ошибка запроса к AmoCrm")
        res.raise_for_status()
        return res

    def refresh_auth(self):
        config = self.get_config()
        url = self.AUTH_URL
        headers = {"Content-Type": "application/json"}
        data = {
            "client_id": config.client_id,
            "client_secret": config.client_secret,
            "grant_type": "refresh_token",
            "refresh_token": config.refresh_token,
            "redirect_uri": config.redirect_uri,
        }
        if settings.DEBUG:
            raise Exception("Токен протух, забери из дева новый")
        res = self.req.post(url, json=data, cookies=self.req.cookies, headers=headers)
        res.raise_for_status()
        res_data = res.json()
        config.refresh_token = res_data["refresh_token"]
        config.access_token = res_data["access_token"]
        config.save()

    def get_contacts(self):
        res = self.request_get("contacts")
        if res.status_code == 204:
            return []
        return res.json()["_embedded"]["items"]

    def find_contacts(self, phone):
        phone = phone[-10:]
        res = self.request_get(f"contacts?query={phone}")
        if res.status_code == 204:
            return []
        return res.json()["_embedded"]["items"]

    def get_pipelines(self):
        res = self.request_get("pipelines")
        return res.json()["_embedded"]["items"]

    def get_lead(self, lead_id):
        res = self.request_get(f"leads?id={lead_id}")
        if res.status_code == 204:
            return None
        return res.json()["_embedded"]["items"][0]

    def create_contact(self, name, phone, resp_user_id=None):
        data = {
            "add": [
                {
                    "name": name,
                    "created_at": int(now().timestamp()),
                    "updated_at": int(now().timestamp()),
                    "tags": self.get_tags(),
                    "custom_fields": [
                        {
                            "id": self.PHONE_FIELD_ID,
                            "values": [{"value": phone, "enum": self.PHONE_FIELD_ENUM}],
                        }
                    ],
                }
            ]
        }
        if resp_user_id:
            resp_user_id = int(resp_user_id)
            data["add"][0]["responsible_user_id"] = resp_user_id

        res = self.request_post("contacts", data)
        return res.json()["_embedded"]["items"][0]["id"]

    def create_task(self, lead_id, resp_user_id=None):
        data = {
            "add": [
                {
                    "element_id": lead_id,
                    "element_type": 2,
                    "task_type": 1,
                    "text": "Связаться",
                    "created_at": int(now().timestamp()),
                    "updated_at": int(now().timestamp()),
                }
            ]
        }
        if resp_user_id:
            resp_user_id = int(resp_user_id)
            data["add"][0]["responsible_user_id"] = resp_user_id

        res = self.request_post("tasks", data)
        return res.json()["_embedded"]["items"][0]["id"]

    def create_note(self, lead_id, text, resp_user_id=None):
        data = {
            "add": [
                {
                    "element_id": lead_id,
                    "element_type": 2,
                    "note_type": 4,
                    "text": text,
                    "created_at": int(now().timestamp()),
                }
            ]
        }
        if resp_user_id:
            resp_user_id = int(resp_user_id)
            data["add"][0]["responsible_user_id"] = resp_user_id

        res = self.request_post("notes", data)
        return res.json()["_embedded"]["items"][0]["id"]

    def create_lead(
        self,
        contact_id,
        pipeline_status_id,
        pipeline_id,
        custom_fields: list,
        description=None,
        resp_user_id=None,
        name_lead=None,
    ):
        custom_fields.append({"id": self.DESC_FIELD_ID, "values": [{"value": description}]})
        data = {
            "add": [
                {
                    "name": name_lead if name_lead else "Сделка",
                    "created_at": int(now().timestamp()),
                    "updated_at": int(now().timestamp()),
                    "status_id": pipeline_status_id,
                    "pipeline_id": pipeline_id,
                    "tags": self.get_tags(),
                    "contacts_id": [contact_id],
                    "custom_fields": custom_fields,
                }
            ]
        }
        if resp_user_id:
            resp_user_id = int(resp_user_id)
            data["add"][0]["responsible_user_id"] = resp_user_id
        res = self.request_post("leads", data)
        return res.json()["_embedded"]["items"][0]["id"]

    @classmethod
    def get_custom_fields(
        cls,
        property_type=None,
        project_enum=None,
        project_name=None,
        roistat_visit=None,
        smart_visitor_id=None,
        smart_session_id=None,
        utm_data=None,
        metrika_cid=None,
        google_cid=None,
        city_name=None,
        email=None,
        url_address=None,
    ) -> list:
        custom_fields = []
        if roistat_visit:
            custom_fields.append({"id": cls.ROISTAT_ID, "values": [{"value": int(roistat_visit)}]})
        if city_name:
            custom_fields.append(
                {"id": cls.CITY_NAME_ID, "values": [cls.CITY_NAME_VALUES.get(city_name)]}
            )
        if property_type:
            custom_fields.append(
                {
                    "id": cls.PROP_TYPE_FIELD_ID,
                    "values": [cls.PROP_TYPE_FIELD_VALUES[property_type]],
                }
            )
        if project_name and project_enum:
            custom_fields.append(
                {"id": cls.PROJ_FIELD_ID, "values": [{"value": project_name, "enum": project_enum}]}
            )
        if smart_session_id:
            custom_fields.append(
                {"id": cls.SMART_SESSION_ID, "values": [{"value": smart_session_id}]}
            )
        if smart_visitor_id:
            custom_fields.append(
                {"id": cls.SMART_VISITOR_ID, "values": [{"value": smart_visitor_id}]}
            )
        if metrika_cid:
            custom_fields.append({"id": cls.METRIKA_CID, "values": [{"value": metrika_cid}]})
        if google_cid:
            custom_fields.append({"id": cls.GOOGLE_CID, "values": [{"value": google_cid}]})
        if utm_data:
            custom_fields.append(
                {"id": cls.UTM_TERM, "values": [{"value": utm_data.get("utm_term", "")}]}
            )
            custom_fields.append(
                {"id": cls.UTM_SOURCE, "values": [{"value": utm_data.get("utm_source", "")}]}
            )
            custom_fields.append(
                {"id": cls.UTM_MEDIUM, "values": [{"value": utm_data.get("utm_medium", "")}]}
            )
            custom_fields.append(
                {"id": cls.UTM_CONTENT, "values": [{"value": utm_data.get("utm_content", "")}]}
            )
            custom_fields.append(
                {"id": cls.UTM_CAMPAIGN, "values": [{"value": utm_data.get("utm_campaign", "")}]}
            )
            if email:
                custom_fields.append({"id": cls.EMAIL_ID, "values": [{"value": email}]})
        if url_address:
            custom_fields.append({"id": cls.URL_FIELD_ID, "values": [{"value": url_address}]})
        print(custom_fields)
        return custom_fields

    def update_lead(self, lead_id, description, custom_fields: list, resp_user_id=None):
        lead = self.get_lead(lead_id)
        if lead is None:
            raise ValueError("Lead not found")

        desc_fields = list(
            filter(lambda field: field["id"] == self.DESC_FIELD_ID, lead["custom_fields"])
        )
        if desc_fields:
            old_description = desc_fields[0]["values"][0]["value"]
        else:
            old_description = ""
        new_description = old_description + "; " + description
        custom_fields.append({"id": self.DESC_FIELD_ID, "values": [{"value": new_description}]})

        data = {
            "update": [
                {
                    "id": lead_id,
                    "updated_at": int(now().timestamp()),
                    "tags": self.get_tags(old_tags=lead["tags"]),
                    "custom_fields": custom_fields,
                }
            ]
        }
        if resp_user_id:
            resp_user_id = int(resp_user_id)
            data["update"][0]["responsible_user_id"] = resp_user_id
        res = self.request_post("leads", data)
        return res.json()["_embedded"]["items"][0]["id"]

    def update_lead_resp_user(self, lead_id, resp_user_id):
        data = {"update": [{"id": lead_id, "updated_at": int(now().timestamp())}]}
        if resp_user_id:
            resp_user_id = int(resp_user_id)
            data["update"][0]["responsible_user_id"] = resp_user_id

        res = self.request_post("leads", data)
        return res.json()["_embedded"]["items"][0]["id"]

    def create_contact_and_lead(
        self,
        name,
        phone,
        description,
        pipeline_status_id,
        pipeline_id,
        text=None,
        resp_user_id=None,
        name_lead=None,
        custom_fields=None,
    ):
        contacts = self.find_contacts(phone)
        if len(contacts) > 0:
            contact = contacts[0]
            contact_resp_user_id = contact["responsible_user_id"]
            contact_id = contact["id"]
            lead_id = contact["leads"]["id"][0] if contact["leads"] else None
            lead_id = (
                lead_id
                if lead_id and self.get_lead(lead_id)["status_id"] not in [142, 143]
                else None
            )
        else:
            contact_id = self.create_contact(name, phone, resp_user_id)
            contact_resp_user_id = None
            lead_id = None

        if lead_id is None:
            lead_id = self.create_lead(
                contact_id,
                pipeline_status_id,
                pipeline_id,
                custom_fields,
                description=description,
                resp_user_id=resp_user_id,
                name_lead=name_lead,
            )
            contact_resp_user_id = self.get_lead(lead_id)["responsible_user_id"]
        create_task.apply_async(args=(lead_id, contact_resp_user_id), countdown=7)
        update_lead.apply_async(args=(lead_id, description, custom_fields), countdown=10)
        if text:
            create_note.apply_async(args=(lead_id, text, resp_user_id), countdown=13)

    def get_tasks(self, path, filter):
        """Получение задач"""
        res = self.request_get_v4(f"{path}?{filter}")
        if res.status_code == 204:
            return None
        return res.json()
