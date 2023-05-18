from urllib import request
import requests
from celery import shared_task
from django.apps import apps
from django.core.files.base import ContentFile
from django.core.cache import cache


@shared_task
def save_remote_image(app_label, model, pk, attr_name, url):
    statuses = (200, 201, 204, 300, 301, 302, 400, 401, 403, 404)

    model = apps.get_model(app_label, model)
    obj = model.objects.get(pk=pk)

    if not url:
        raise ValueError("url is empty")
    if not hasattr(obj, attr_name):
        raise AttributeError(f"{obj} has no attribute {attr_name}")

    attr = getattr(obj, attr_name)

    status = 0
    tries = 0

    while status not in statuses and tries < 100:

        tries += 1

        response = requests.get(url)

        status = response.status_code

        if status == 200:

            image = ContentFile(response.content)
            filename = request.urlparse(url).path.split("/")[-1]
            attr.save(filename, image)

            break


@shared_task
def cache_set(cache_name, result, timeout):
    cache.set(cache_name, result, timeout)
