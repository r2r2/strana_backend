from django.db import models


class DocumentCategory(models.Model):
    """
    Категория документа
    """

    title = models.CharField(verbose_name="Заголовок", max_length=200)
    order = models.PositiveSmallIntegerField(verbose_name="Очередность", default=0)

    def __str__(self) -> str:
        return self.title

    class Meta:
        verbose_name = "Категория документа"
        verbose_name_plural = "Категории докуметов"
        ordering = ("order",)
