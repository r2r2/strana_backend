from django.db import models


class BookingSettings(models.Model):
    """
    Настройки бронирования
    """
    name = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        verbose_name="Название",
    )
    default_flats_reserv_time = models.FloatField(
        default=24,
        null=True,
        blank=True,
        verbose_name="Время резервирования квартир по умолчанию (ч)",
        help_text="Определяет время бесплатного резервирования квартиры "
                  "для агента по умолчанию (если не задано в проекте и корпусе)"
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Дата обновления")

    def __str__(self):
        return self.name if self.name else str(self.id)

    class Meta:
        managed = False
        db_table = 'settings_booking_settings'
        verbose_name = "Настройки бронирования"
        verbose_name_plural = "Настройки бронирования"
