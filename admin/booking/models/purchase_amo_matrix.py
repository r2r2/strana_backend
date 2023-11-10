from django.db import models


class PurchaseAmoMatrix(models.Model):
    """
    Матрица способов оплаты при взаимодействии с АМО.
    """

    payment_method = models.ForeignKey(
        "booking.PaymentMethod",
        on_delete=models.CASCADE,
        related_name="purchase_amo_matrix",
        verbose_name="Способ оплаты",
        help_text="Способ оплаты",
    )
    mortgage_type = models.ForeignKey(
        "properties.MortgageType",
        on_delete=models.CASCADE,
        related_name="purchase_amo_matrix",
        verbose_name="Тип ипотеки",
        null=True,
        blank=True,
    )
    amo_payment_type = models.IntegerField(verbose_name="ID Значения в АМО для типа оплаты")
    default: bool = models.BooleanField(default=False, verbose_name="По умолчанию")
    priority: int = models.IntegerField(default=0, verbose_name="Приоритет")

    def __str__(self):
        return str(self.amo_payment_type)

    class Meta:
        managed = False
        db_table = "payments_purchase_amo_matrix"
        verbose_name = "Матрица способов оплаты при взаимодействии с АМО."
        verbose_name_plural = "1.14. [Справочник] Матрицы способов оплаты при взаимодействии с АМО."
