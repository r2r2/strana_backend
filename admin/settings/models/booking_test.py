from django.db import models
from django.utils.translation import gettext_lazy as _


class TestBooking(models.Model):
    """
    Тестовые бронирования
    """

    class TestBookingStatus(models.TextChoices):
        """
        Статус тестового бронирования
        """
        IN_AMO: str = "in_amo", _("Есть в АМО (не удалена)")
        NOT_IN_AMO: str = "not_in_amo", _("Нет в АМО (удалена)")

    booking: models.ForeignKey = models.ForeignKey(
        to="booking.Booking",
        related_name="booking_test",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Сделка",
    )
    amocrm_id = models.CharField(
        max_length=50,
        verbose_name="AMO CRM ID",
        db_index=True,
    )
    status = models.CharField(
        choices=TestBookingStatus.choices,
        max_length=20,
        verbose_name="Статус",
        help_text="Статус сделки",
        db_index=True,
    )
    info: str | None = models.TextField(verbose_name="Примечание", null=True, blank=True)
    last_check_at = models.DateTimeField(verbose_name="Дата последней проверки", blank=True, null=True)
    is_check_skipped: bool = models.BooleanField(verbose_name="Исключить из проверки", default=False)

    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Дата обновления")

    def __str__(self):
        return str(self.id)

    class Meta:
        managed = False
        db_table = 'booking_testbooking'
        verbose_name = "Тестовое бронирование"
        verbose_name_plural = "15.6. Тестовые бронирования"
