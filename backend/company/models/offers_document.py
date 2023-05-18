from django.db import models


class OffersDocument(models.Model):
    """
    Документы оферты и политика обработки данных
    """

    cities = models.ManyToManyField(verbose_name="Города", to="cities.City", blank=True)
    file = models.FileField(verbose_name="Файл", upload_to="c/od/f")

    def __str__(self) -> str:
        return str(self.file)

    class Meta:
        verbose_name = "Доументы оферты и политика обработки данных"
        verbose_name_plural = "Доументы оферты и политика обработки данных"
