import os
import requests


def export_in_amo(instanse_type, pk):
    SITE_HOST = os.getenv("LK_SITE_HOST")
    DEBUG = os.getenv("DEBUG")
    EXPORT_CABINET_KEY = os.getenv("EXPORT_CABINET_KEY", default="default_key")

    update_link = f"http://{SITE_HOST}/api/{instanse_type}/superuser/fill/{pk}"
    payload = {'data': EXPORT_CABINET_KEY}
    if DEBUG == "False":
        requests.patch(update_link, params=payload)
