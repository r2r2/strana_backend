from ckeditor.fields import RichTextField
from django.db import models


class Tender(models.Model):
    """
    Тендер
    """

    title = models.CharField(verbose_name="Название", max_length=200)
    announcement = RichTextField(verbose_name="Анонс", blank=True)
    descriptions = RichTextField(verbose_name="Описание", blank=True)
    order = models.PositiveIntegerField(verbose_name="Очередность", default=0)

    city = models.ForeignKey(verbose_name="Город", to="cities.City", on_delete=models.CASCADE)
    category = models.ForeignKey(
        verbose_name="Категория", to="company.TenderCategory", on_delete=models.CASCADE
    )

    def __str__(self) -> str:
        return self.title

    class Meta:
        verbose_name = "Тендер"
        verbose_name_plural = "Тендеры"
        ordering = ("order",)
