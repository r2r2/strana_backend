from django.db import models

from common.models import MultiImageMeta, Spec
from . import Property

__all__ = ["PropertyCommercialGallery"]


class PropertyCommercialGallery(models.Model, metaclass=MultiImageMeta):
    IMAGE_WIDTH = 1920
    IMAGE_HEIGHT = 1080

    property = models.ForeignKey(to=Property, on_delete=models.CASCADE)
    image = models.ImageField("Изображение", upload_to="b/bcg/i/", blank=True, null=True)
    order = models.PositiveSmallIntegerField(verbose_name="Порядок", default=0)
    image_map = {
        "image_display": Spec(source="image", width=IMAGE_WIDTH, height=IMAGE_HEIGHT),
        "image_preview": Spec(source="image", width=IMAGE_WIDTH, height=IMAGE_HEIGHT, blur=True),
    }

    class Meta:
        ordering = ("order",)
        verbose_name = "Изображение для коммерческого помещения"
        verbose_name_plural = "Галерея для коммерческих помещений"

    def __str__(self):
        return f"{self.property.__str__()}: Изображение №{self.order}, {self.image.name}"
