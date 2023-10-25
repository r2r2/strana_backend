from django.db import models


class MortgageType(models.Model):
    """
    Тип ипотеки
    """

    title = models.CharField(max_length=100, null=True, verbose_name="Название")
    amocrm_id: int | None = models.BigIntegerField(verbose_name="ID в AmoCRM", null=True, unique=True)

    def __str__(self) -> str:
        return self.title if self.title else "-"

    class Meta:
        managed = False
        db_table = "payments_mortgage_types"
        verbose_name = "Тип ипотеки"
        verbose_name_plural = "3.9. [Справочник] Тип ипотеки"
