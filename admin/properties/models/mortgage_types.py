from django.db import models


class MortgageType(models.Model):
    """
    Тип ипотеки
    """

    title = models.CharField(max_length=100, null=True, verbose_name="Название")
    amocrm_id: int | None = models.BigIntegerField(verbose_name="ID в AmoCRM", null=True, blank=True, unique=True)
    by_dev: bool = models.BooleanField(default=False, verbose_name="Субсидированная ипотека")
    slug = models.CharField(
        max_length=50,
        unique=True,
        verbose_name="Слаг",
        null=True,
        blank=True,
    )

    def __str__(self) -> str:
        return self.title if self.title else "-"

    class Meta:
        managed = False
        db_table = "payments_mortgage_types"
        verbose_name = "Тип ипотеки"
        verbose_name_plural = "3.9. [Справочник] Тип ипотеки"
