import os
import requests
import json

from django.forms import JSONField


def export_in_amo(instanse_type, pk):
    SITE_HOST = os.getenv("LK_SITE_HOST")
    DEBUG = os.getenv("DEBUG")
    EXPORT_CABINET_KEY = os.getenv("EXPORT_CABINET_KEY", default="default_key")

    update_link = f"http://{SITE_HOST}/api/{instanse_type}/superuser/fill/{pk}"
    payload = {'data': EXPORT_CABINET_KEY}
    if DEBUG == "False":
        requests.patch(update_link, params=payload)


class ReadableJSONFormField(JSONField):
    def prepare_value(self, value):
        return json.dumps(value, ensure_ascii=False)
