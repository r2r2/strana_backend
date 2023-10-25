from django.db import models


class PriceSchema(models.Model):
    """
    Схема сопоставление цен в матрице
    """

    price_type = models.ForeignKey(
        "properties.PropertyPriceType",
        models.SET_NULL,
        related_name="price_schema",
        null=True,
        blank=True,
        verbose_name="Тип цены",
        help_text="Тип цены",
    )
    slug = models.CharField(
        max_length=15,
        null=True,
        blank=True,
        verbose_name="slug поля цены из Profit base",
    )

    def __str__(self) -> str:
        return (
            f"{self.price_type} {self.slug}"
            if self.price_type and self.slug
            else self.id
        )

    class Meta:
        managed = False
        db_table = "payments_price_schema"
        verbose_name = "схема сопоставление"
        verbose_name_plural = "1.15. Схема сопоставление цен в матрице"
