from django.db import models


class TenderCategory(models.Model):
    """
    Категория тендера
    """

    title = models.CharField(verbose_name="Название", max_length=200)
    order = models.PositiveSmallIntegerField(verbose_name="Очередность", default=0)

    def __str__(self) -> str:
        return self.title

    class Meta:
        verbose_name = "Категория тендеров"
        verbose_name_plural = "Категории тендеров"
        ordering = ("order",)
