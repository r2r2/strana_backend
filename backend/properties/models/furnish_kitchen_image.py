from django.db import models
from common.models import OrderedImage, MultiImageMeta, Spec


class FurnishKitchenImage(OrderedImage, metaclass=MultiImageMeta):
    """
    Изображение отделки кухни
    """

    WIDTH = 2880
    HEIGHT = 1620
    upload_to = "p/furnish_kitchen"

    furnish = models.ForeignKey(
        verbose_name="Отделка кухни",
        to="properties.FurnishKitchen",
        on_delete=models.CASCADE,
        related_name="image_set",
    )
    category = models.ForeignKey(
        verbose_name="Категория",
        to="properties.FurnishKitchenCategory",
        on_delete=models.CASCADE,
        related_name="image_set",
        null=True,
        blank=True,
    )

    project = models.ManyToManyField(
        verbose_name="Проект",
        to="projects.Project",
        blank=True,
    )

    image_map = {
        "file_display": Spec(source="file", width=WIDTH, height=HEIGHT),
        "file_preview": Spec(source="file", width=WIDTH, height=HEIGHT, blur=True),
    }

    def __str__(self) -> str:
        return f"{self.furnish} - Изображение {self.id}"

    class Meta(OrderedImage.Meta):
        verbose_name = "Изображение отделки кухни"
        verbose_name_plural = "Изображения отделки кухни"
        ordering = ("order",)
