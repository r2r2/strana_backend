import datetime
import os
import requests
import zlib


def export_in_amo(instanse_type, pk):
    SITE_HOST = os.getenv("LK_SITE_HOST")
    DEBUG = os.getenv("DEBUG")

    update_link = f"http://{SITE_HOST}/api/{instanse_type}/superuser/fill/{pk}"
    # хэшируем текущую дату и отправляем хеш гет параметром (закрываем апи от случайных гостей)
    today_date = bytes(str(datetime.datetime.now().date()), 'utf-8')
    payload = {'data': zlib.crc32(today_date)}
    if DEBUG == "False":
        requests.patch(update_link, params=payload)
