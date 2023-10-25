import os
import requests
import json
from http import HTTPStatus

from django.forms import JSONField

DOCKER_SITE_HOST = os.getenv("LK_DOCKER_SITE_HOST", "http://cabinet:1800")
SITE_HOST = os.getenv("LK_SITE_HOST")
DEBUG = os.getenv("DEBUG")
EXPORT_CABINET_KEY = os.getenv("EXPORT_CABINET_KEY", default="default_key")


def export_in_amo(instanse_type, pk):
    update_link = f"https://{SITE_HOST}/api/{instanse_type}/superuser/fill/{pk}"
    payload = {'data': EXPORT_CABINET_KEY}

    if DEBUG == "False":
        requests.patch(update_link, params=payload)


class ReadableJSONFormField(JSONField):
    def prepare_value(self, value):
        return json.dumps(value, ensure_ascii=False)


def get_client_token_from_cabinet(client_id):
    get_client_token_link = f"{DOCKER_SITE_HOST}/api/auth/superuser_get_client_token"
    requests.post(url=get_client_token_link, json=dict(client_id=client_id))


def import_clients_and_booking_from_amo(broker_id):
    import_clients_and_booking_from_amo_link = f"{DOCKER_SITE_HOST}/api/users/import_clients_and_bookings_from_amo"
    response = requests.post(url=import_clients_and_booking_from_amo_link, json=dict(broker_id=broker_id))

    if response.status_code == HTTPStatus.OK:
        return True
    else:
        return False
