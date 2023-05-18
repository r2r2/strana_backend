from django.db import models


class VacancyFormat(models.Model):
    """
    Формат работы(офис, удаленно, ...)
    """

    name = models.CharField(verbose_name="Название", max_length=50)

    class Meta:
        verbose_name = "Формат работы"
        verbose_name_plural = "Форматы работы"

    def __str__(self) -> str:
        return self.name
