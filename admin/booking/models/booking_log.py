# pylint: disable=no-member
from common.loggers.models import AbstractLog
from django.db import models


class BookingLog(AbstractLog):
    booking = models.ForeignKey(
        "booking.Booking",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        verbose_name="Бронирование",
        db_index=True,
    )

    def __str__(self):
        return f"{self.use_case} – {self.content}" if self.use_case and self.content else self

    class Meta:
        db_table = "booking_bookinglog"
        verbose_name = "Лог: "
        verbose_name_plural = " 1.6. [Логи] Логи бронирований"
