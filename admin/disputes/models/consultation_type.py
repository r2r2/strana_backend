from django.db import models


class ConsultationType(models.Model):
    """
    Справочник типов консультаций
    """

    name: str = models.CharField(max_length=30, verbose_name="Название", null=False)
    slug: str = models.CharField(max_length=30, verbose_name="Слаг", null=False)
    priority: int = models.IntegerField(verbose_name="Приоритет", default=0)

    def __str__(self):
        return self.name

    class Meta:
        db_table = "users_consultation_type"
        verbose_name = "Тип консультации"
        verbose_name_plural = "6.9. [Справочник] Тип консультации"
        ordering = ["priority"]
