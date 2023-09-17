from django.db import models


class BookingSource(models.Model):
    """
    Источник бронирования
    """
    name: str = models.CharField(
        max_length=100,
        verbose_name="Название источника",
    )
    slug: str = models.CharField(
        max_length=100,
        verbose_name="Слаг источника",
    )

    def __str__(self) -> str:
        return self.name

    class Meta:
        managed = False
        db_table = 'booking_source'
        verbose_name = 'Источник бронирования'
        verbose_name_plural = '1.9.3  Источники бронирования'
