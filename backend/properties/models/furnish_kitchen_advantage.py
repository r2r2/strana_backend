from ajaximage.fields import AjaxImageField

from django.db import models
from common.models import MultiImageMeta, Spec


class FurnishKitchenAdvantage(models.Model, metaclass=MultiImageMeta):

    WIDTH = 1200
    HEIGHT = 1560

    order = models.PositiveSmallIntegerField(
        verbose_name="Порядок", default=1
    )
    description = models.TextField(
        verbose_name="Описание",
    )
    image = AjaxImageField(
        verbose_name="Изображение", upload_to="f/kitchen/advantage"
    )
    furnish = models.ForeignKey(
        to="properties.FurnishKitchen", verbose_name="Отделка кухни",
        on_delete=models.CASCADE
    )
    image_map = {
        "image_display": Spec(source="image", width=WIDTH, height=HEIGHT),
        "image_preview": Spec(source="image", width=WIDTH, height=HEIGHT, blur=True),
    }

    class Meta:
        verbose_name = "Преимущество отделки кухни"
        verbose_name_plural = "Преимущества отделки кухни"
        ordering = ("order",)
