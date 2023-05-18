from django.db import models
from common.models import OrderedImage, MultiImageMeta, Spec


class FurnishImage(OrderedImage, metaclass=MultiImageMeta):
    """
    Изображение отделки
    """
    WIDTH = 2880
    HEIGHT = 1620
    upload_to = "p/furnish"
    title = models.CharField(
        max_length=255, blank=True, default="",
        verbose_name="Заголовок"
    )
    description = models.TextField(
        blank=True, default="",
        verbose_name="Текст изображения"
    )
    furnish = models.ForeignKey(
        verbose_name="Отделка",
        to="properties.Furnish",
        on_delete=models.CASCADE,
        related_name="image_set",
    )
    category = models.ForeignKey(
        verbose_name="Категория",
        to="properties.FurnishCategory",
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
        verbose_name = "Изображение отделки"
        verbose_name_plural = "Изображения отделки"
        ordering = ("order",)
