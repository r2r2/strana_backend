from ckeditor.fields import RichTextField
from django.db import models


class FurnishCategory(models.Model):
    """
    Категория отделки
    """

    title = models.CharField(verbose_name="Заголовок", max_length=100)
    text = RichTextField(verbose_name="Текст", max_length=1000)
    order = models.PositiveSmallIntegerField(verbose_name="Порядок")

    def __str__(self) -> str:
        return self.title

    class Meta:
        verbose_name = "Категория отделки"
        verbose_name_plural = "Категории отделки"
        ordering = ("order",)
