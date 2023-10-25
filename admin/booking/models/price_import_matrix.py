from django.db import models


class PriceImportMatrix(models.Model):
    """
    Матрица сопоставления цен при импорте объекта
    """

    cities: models.ManyToManyField = models.ManyToManyField(
        to="references.Cities",
        through="booking.PriceImportMatrixCitiesThrough",
        verbose_name="Города",
        related_name="import_matrix",
        help_text="Города",
    )
    price_schema: models.ForeignKey = models.OneToOneField(
        to="booking.PriceSchema",
        verbose_name="Сопоставление цен",
        related_name="price_schema",
        null=True,
        on_delete=models.SET_NULL,
    )
    default: bool = models.BooleanField(default=False, verbose_name="По умолчанию")

    def __str__(self):
        return f"Матрица для {self.price_schema}" if self.price_schema else self.id

    class Meta:
        managed = False
        db_table = "payments_price_import_matrix"
        verbose_name = "матрица сопоставления"
        verbose_name_plural = "1.14. Матрица сопоставления цен при импорте объекта"


class PriceImportMatrixCitiesThrough(models.Model):
    import_price = models.OneToOneField(
        verbose_name="Статус",
        to="booking.PriceImportMatrix",
        on_delete=models.CASCADE,
        related_name="price_import",
        primary_key=True,
    )
    city = models.ForeignKey(
        verbose_name="Действие",
        to="references.Cities",
        on_delete=models.CASCADE,
        unique=False,
        related_name="price_import_city",
    )

    class Meta:
        managed = False
        db_table = "payments_price_import_matrix_cities"
