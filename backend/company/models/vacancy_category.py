from django.db import models


class VacancyCategory(models.Model):
    """
    Категория вакансии
    """

    name = models.CharField(verbose_name="Название", max_length=200)
    order = models.PositiveIntegerField(verbose_name="Очередность", default=0)

    def __str__(self) -> str:
        return self.name

    class Meta:
        verbose_name = "Категория вакансии"
        verbose_name_plural = "Категории вакансий"
        ordering = ("order",)
