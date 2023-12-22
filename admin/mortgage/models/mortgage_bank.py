from django.db import models


class MortgageBank(models.Model):
    """
    Банки под ипотечный калькулятор.
    """
    name: str = models.CharField(
        verbose_name="Название",
        max_length=255,
    )
    icon: models.FileField = models.FileField(
        verbose_name="Иконка",
        null=True,
        blank=True,
    )
    priority: int = models.IntegerField(
        verbose_name="Приоритет",
        default=0,
    )
    external_code: str = models.TextField(
        verbose_name="Внешний код",
    )
    uid: str = models.CharField(
        verbose_name="UID",
        max_length=255,
        null=True,
        blank=True,
    )

    def __str__(self) -> str:
        return self.name

    class Meta:
        managed = False
        db_table = 'mortgage_calculator_banks'
        verbose_name = "Банк"
        verbose_name_plural = "21.5 Банки"
