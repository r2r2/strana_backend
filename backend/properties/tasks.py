import requests
from celery import shared_task
from django.contrib.contenttypes.models import ContentType
from django.core.files.base import ContentFile

from .services import (
    update_layouts,
    update_special_offers_activity,
    update_layout_min_mortgage,
    update_properties_min_mortgage,
    update_price_with_special_offers,
    update_layouts_facing_by_property,
)
from common.imgproxy import ImageProxy


@shared_task
def convert_to_png(app_label, model, pk, to_attr, url, width, height) -> None:
    ct = ContentType.objects.get_by_natural_key(app_label, model)
    obj = ct.get_object_for_this_type(pk=pk)
    if not url:
        raise ValueError("url is empty")
    if not hasattr(obj, to_attr):
        raise AttributeError(f"{obj} has no attribute {to_attr}")
    attr = getattr(obj, to_attr)
    url = ImageProxy(source=url, width=width, height=height).svg_to_png_url()
    if not url:
        return
    g = requests.get(url)
    print(requests.get(f"http://imageproxy:8080/"))
    g.raise_for_status()
    image = ContentFile(g.content)
    filename = f"{obj.id}_plan_png.png"
    attr.save(filename, image)


@shared_task
def update_layouts_task() -> None:
    update_layouts()


@shared_task
def update_layout_min_mortgage_task(layout_id: int) -> None:
    update_layout_min_mortgage(layout_id)


@shared_task
def update_special_offers_activity_task() -> None:
    update_special_offers_activity()


@shared_task
def update_properties_min_mortgage_task() -> None:
    update_properties_min_mortgage()


@shared_task
def update_price_with_special_offers_task() -> None:
    update_price_with_special_offers()


@shared_task
def update_layouts_facing_by_property_task() -> None:
    update_layouts_facing_by_property()
