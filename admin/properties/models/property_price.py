from django.db import models


class PropertyPriceType(models.Model):
    """
    Тип цены объекта недвижимости
    """
    name = models.CharField(max_length=100, null=True, verbose_name="Название")
    default: bool = models.BooleanField(default=False, verbose_name="Тип по умолчанию")
    slug = models.CharField(max_length=15, unique=True, null=True, verbose_name="slug для импорта с портала")

    def __str__(self) -> str:
        return self.name

    class Meta:
        managed = False
        db_table = "payments_property_price_type"
        verbose_name = "Тип цены объекта недвижимости"
        verbose_name_plural = "3.7. [Справочник] Типы цен объекта недвижимости"


class PropertyPrice(models.Model):
    """
    Цена объекта недвижимости
    """
    property = models.ForeignKey(
        to="properties.Property",
        related_name='property_prices',
        on_delete=models.CASCADE,
        verbose_name="Объект недвижимости",
    )
    price = models.DecimalField(verbose_name="Цена", max_digits=10, decimal_places=2, null=True)
    price_type = models.ForeignKey(
        "properties.PropertyPriceType",
        on_delete=models.CASCADE,
        related_name="property_prices",
        verbose_name="Тип цены",
    )

    def __str__(self) -> str:
        return f"{self.price} типа {self.price_type}"

    class Meta:
        managed = False
        db_table = "payments_property_price"
        verbose_name = "Цена объекта недвижимости"
        verbose_name_plural = "3.8. [Справочник] Цены объекта недвижимости"
