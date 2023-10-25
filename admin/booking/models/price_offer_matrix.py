from django.db import models


class PriceOfferMatrix(models.Model):
    """
    Матрица предложения цены
    """
    name = models.CharField(max_length=100, null=True, verbose_name="Название")
    payment_method = models.ForeignKey(
        "booking.PaymentMethod",
        on_delete=models.SET_NULL,
        related_name="payment_method",
        verbose_name="Способ оплаты",
        help_text="Способ оплаты",
        null=True,
    )
    by_dev: bool = models.BooleanField(default=False, verbose_name="Субсидированная ипотека")
    price_type = models.ForeignKey(
        "properties.PropertyPriceType",
        on_delete=models.CASCADE,
        related_name="price_type",
        verbose_name="Тип цены",
    )
    priority: int = models.IntegerField(default=0, verbose_name="Приоритет")

    def __str__(self):
        return self.name

    class Meta:
        managed = False
        db_table = "payments_price_offer_matrix"
        verbose_name = "Матрица предложения цены"
        verbose_name_plural = "1.12. [Справочник] Матрицы предложения цены"
