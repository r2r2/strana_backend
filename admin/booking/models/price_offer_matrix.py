from django.db import models


class PriceOfferMatrix(models.Model):
    """
    Матрица предложения цены
    """
    name = models.CharField(max_length=100, null=True, verbose_name="Название")
    payment_method = models.ForeignKey(
        "booking.PaymentMethod",
        on_delete=models.CASCADE,
        related_name="price_offer",
        verbose_name="Способ оплаты",
        help_text="Способ оплаты",
        null=True,
        blank=True,
    )
    default: bool = models.BooleanField(default=False, verbose_name="По умолчанию")
    price_type = models.ForeignKey(
        "properties.PropertyPriceType",
        on_delete=models.SET_NULL,
        related_name="price_offer",
        verbose_name="Тип цены",
        null=True,
        blank=True,
    )
    mortgage_type = models.ForeignKey(
        to="properties.MortgageType",
        on_delete=models.CASCADE,
        related_name="price_offer",
        verbose_name="Тип ипотеки",
        null=True,
        blank=True,
    )
    priority: int = models.IntegerField(default=0, verbose_name="Приоритет")

    def __str__(self):
        return self.name

    class Meta:
        managed = False
        db_table = "payments_price_offer_matrix"
        verbose_name = "Матрица предложения цены"
        verbose_name_plural = "1.12. [Справочник] Матрицы предложения цены"
