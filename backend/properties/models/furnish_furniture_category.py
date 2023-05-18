from ckeditor.fields import RichTextField
from django.db import models


class FurnishFurnitureCategory(models.Model):
    """
    Категория отделки мебели
    """

    title = models.CharField(verbose_name="Заголовок", max_length=100)
    text = RichTextField(verbose_name="Текст", max_length=1000)
    order = models.PositiveSmallIntegerField(verbose_name="Порядок")

    def __str__(self) -> str:
        return self.title

    class Meta:
        verbose_name = "Категория отделки мебели"
        verbose_name_plural = "Категории отделки мебели"
        ordering = ("order",)
