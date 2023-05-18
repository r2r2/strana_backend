from django.db import models
from ckeditor.fields import RichTextField
from common.fields import PpoiField


class FurnishKitchenPoint(models.Model):
    """
    Точка на изображении отделки кухни
    """

    point = PpoiField(verbose_name="Точка", source="image.file", null=True, blank=True)
    title = models.CharField(verbose_name="Заголовок", blank=True, max_length=100)
    text = RichTextField(verbose_name="Текст", max_length=1000)
    image = models.ForeignKey(
        verbose_name="Отделка",
        to="properties.FurnishKitchenImage",
        on_delete=models.CASCADE,
        related_name="point_set",
    )
    order = models.PositiveIntegerField(verbose_name="Порядок", default=0, db_index=True)

    def __str__(self) -> str:
        return f"{self.point} - {self.image}"

    class Meta:
        verbose_name = "Точка на изображении отделки кухни"
        verbose_name_plural = "Точка на изображении отделки кухни"
        ordering = ("order",)
