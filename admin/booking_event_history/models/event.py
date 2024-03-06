from django.db import models
from django.core.exceptions import ValidationError


class BookingEvent(models.Model):
    event_name: str = models.CharField(
        verbose_name="Название",
        max_length=150,
    )
    event_description: str = models.TextField(verbose_name="Описание", null=True, blank=True)
    slug: str = models.CharField(
        verbose_name="Слаг",
        max_length=100,
    )
    event_type = models.ForeignKey(
        verbose_name="Тип события",
        to="booking_event_history.EventType",
        on_delete=models.CASCADE,
        null=True
    )

    def __str__(self) -> str:
        return f"{self.event_name}"

    class Meta:
        verbose_name = "Событие"
        verbose_name_plural = "23.2 События"
        db_table = "booking_event"
