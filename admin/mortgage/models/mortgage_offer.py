from django.db import models


class MortgageOffer(models.Model):
    """
    Ипотечные предложения.
    """
    name: str = models.CharField(
        max_length=255,
        verbose_name="Название предложения",
        null=True,
        blank=True,
    )
    bank: models.ForeignKey = models.ForeignKey(
        to="mortgage.MortgageBank",
        on_delete=models.CASCADE,
        related_name="mortgage_offers",
        verbose_name="Банк",
        null=True,
        blank=True,
    )
    program: models.ForeignKey = models.ForeignKey(
        to="mortgage.MortgageProgram",
        on_delete=models.CASCADE,
        related_name="mortgage_offers",
        verbose_name="Ипотечная программа",
        null=True,
        blank=True,
    )
    external_code: str = models.TextField(
        verbose_name="Внешний код",
        null=True,
        blank=True,
    )
    monthly_payment: float = models.FloatField(
        verbose_name="Платеж в месяц",
        default=0,
    )
    percent_rate: float = models.FloatField(
        verbose_name="Процентная ставка",
        default=0,
    )
    credit_term: float = models.FloatField(
        verbose_name="Срок кредита",
        default=0,
    )
    uid: str = models.CharField(
        max_length=255,
        verbose_name="Для синхронизации с ДВИЖ",
        null=True,
        blank=True,
    )

    def __str__(self) -> str:
        return self.name

    class Meta:
        managed = False
        db_table = 'mortgage_calculator_offer'
        verbose_name = "Ипотечное предложение"
        verbose_name_plural = "21.7 Ипотечные предложения"
