from datetime import datetime

from tortoise import Model, fields
from typing import TYPE_CHECKING, Optional

from common.orm.mixins import CRUDMixin, ExistsMixin
from src.booking.entities import BaseBookingRepo

if TYPE_CHECKING:
    from src.booking.repos import Booking, BookingEvent, MortgageApplicationArchive, DocumentArchive


class BookingEventHistory(Model):
    """
    23.1 История сделок
    """
    id: int = fields.IntField(description="ID", pk=True)
    booking: fields.ForeignKeyRelation["Booking"] = fields.ForeignKeyField(
        description="Сделка",
        model_name="models.Booking",
        related_name="event_histories",
        on_delete=fields.CASCADE,
    )
    actor: str = fields.CharField(description="Действующее лицо", max_length=150)
    event: fields.ForeignKeyRelation["BookingEvent"] = fields.ForeignKeyField(
        description="Событие",
        model_name="models.BookingEvent",
        related_name="event_histories",
        on_delete=fields.SET_NULL,
        null=True
    )
    event_slug: str = fields.CharField(description="Слаг события", max_length=100)
    date_time: datetime = fields.DatetimeField(description="Время", auto_now_add=True)
    event_type_name: str = fields.CharField(
        description="Название типа события",
        max_length=150
    )
    event_name: str = fields.CharField(
        description="Название события",
        max_length=150
    )
    event_description: Optional[str] = fields.TextField(description="Описание", null=True)

    group_status_until: Optional[str] = fields.CharField(
        description="Групп. статус (Этап) До",
        max_length=150,
        null=True
    )
    group_status_after: Optional[str] = fields.CharField(
        description="Групп. статус (Этап) После",
        max_length=150,
        null=True
    )
    task_name_until: Optional[str] = fields.CharField(
        description="Название задачи До",
        max_length=150,
        null=True
    )
    task_name_after: Optional[str] = fields.CharField(
        description="Название задачи После",
        max_length=150,
        null=True
    )
    signed_offer: fields.ForeignKeyRelation["DocumentArchive"] = fields.ForeignKeyField(
        description="Шаблон подписанной оферты",
        model_name="models.DocumentArchive",
        related_name="event_histories",
        on_delete=fields.SET_NULL,
        null=True
    )
    mortgage_ticket_inform: fields.ForeignKeyRelation["MortgageApplicationArchive"] = fields.ForeignKeyField(
        description="Архив заявки на ипотеку",
        model_name="models.MortgageApplicationArchive",
        related_name="event_histories",
        on_delete=fields.SET_NULL,
        null=True
    )
    event_status_until: Optional[str] = fields.CharField(
        description="Статус встречи До",
        max_length=150,
        null=True
    )
    event_status_after: Optional[str] = fields.CharField(
        description="Статус встречи После",
        max_length=150,
        null=True
    )

    def __str__(self) -> str:
        return f"<{self.event_name} | {self.actor}>"

    class Meta:
        table = "booking_event_history"


class BookingEventHistoryRepo(BaseBookingRepo, CRUDMixin, ExistsMixin):
    """
    Репозиторий истории сделок
    """

    model = BookingEventHistory
