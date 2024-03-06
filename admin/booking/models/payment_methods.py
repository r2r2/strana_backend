from django.db import models


class PaymentMethod(models.Model):
    """
    Способ оплаты
    """
    name = models.CharField(max_length=100, null=True, verbose_name="Название")
    amocrm_id = models.BigIntegerField(blank=True, null=True, verbose_name="AmoCRM ID")
    slug = models.CharField(
        max_length=50,
        unique=True,
        verbose_name="Слаг",
    )

    def __str__(self):
        return self.name

    class Meta:
        managed = False
        db_table = "payments_payment_method"
        verbose_name = "Способ оплаты"
        verbose_name_plural = "1.13. [Справочник] Способы оплаты"
