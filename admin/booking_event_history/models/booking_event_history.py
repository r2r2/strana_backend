from datetime import datetime
from typing import Optional

from django.db import models


class BookingEventHistory(models.Model):
    booking = models.ForeignKey(
        verbose_name="Сделка",
        to="booking.Booking",
        on_delete=models.CASCADE,
    )
    actor: str = models.CharField(verbose_name="Действующее лицо", max_length=150)
    event = models.ForeignKey(
        verbose_name="Событие",
        to="booking_event_history.BookingEvent",
        on_delete=models.SET_NULL,
        null=True
    )
    event_slug: str = models.CharField(verbose_name="Слаг события", max_length=100)
    date_time: datetime = models.DateTimeField(verbose_name="Время", auto_now=True)
    event_type_name: str = models.CharField(
        verbose_name="Название типа события",
        max_length=150
    )
    event_name: str = models.CharField(
        verbose_name="Название события",
        max_length=150
    )
    event_description: Optional[str] = models.TextField(
        verbose_name="Описание",
        null=True,
        blank=True
    )

    group_status_until: Optional[str] = models.CharField(
        verbose_name="Групп. статус (Этап) До",
        max_length=150,
        null=True,
        blank=True
    )
    group_status_after: Optional[str] = models.CharField(
        verbose_name="Групп. статус (Этап) После",
        max_length=150,
        null=True,
        blank=True
    )
    task_name_until: Optional[str] = models.CharField(
        verbose_name="Название задачи До",
        max_length=150,
        null=True,
        blank=True
    )
    task_name_after: Optional[str] = models.CharField(
        verbose_name="Название задачи После",
        max_length=150,
        null=True,
        blank=True
    )
    mortgage_ticket_inform = models.ForeignKey(
        verbose_name="Архив заявки на ипотеку",
        to="booking_event_history.MortgageApplicationArchive",
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    signed_offer = models.ForeignKey(
        verbose_name="Шаблон подписанной оферты",
        to="booking_event_history.DocumentArchive",
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    event_status_until: Optional[str] = models.CharField(
        verbose_name="Статус встречи До",
        max_length=150,
        null=True,
        blank=True
    )
    event_status_after: Optional[str] = models.CharField(
        verbose_name="Статус встречи После",
        max_length=150,
        null=True,
        blank=True
    )

    def __str__(self) -> str:
        return f"{self.event_name} | {self.actor}"

    class Meta:
        verbose_name = "История сделок"
        verbose_name_plural = "23.1 Истории сделок"
        db_table = "booking_event_history"
