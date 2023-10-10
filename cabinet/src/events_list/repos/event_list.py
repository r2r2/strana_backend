from datetime import datetime

from tortoise import Model, fields

from common.orm.mixins import CRUDMixin
from src.events_list.entities import BaseEventListRepo


class EventList(Model):
    """
    Список мероприятий.
    """
    id: int = fields.IntField(description="ID", pk=True)
    name: str = fields.CharField(
        description="Название мероприятия",
        max_length=255,
        null=True,
    )
    token: str = fields.TextField(description="Токен для импорта мероприятия", null=True)
    event_date: datetime = fields.DatetimeField(
        description="Дата и время мероприятия",
        null=True,
    )
    title: str = fields.CharField(
        description="Заголовок в модальном окне",
        max_length=255,
        null=True,
    )
    subtitle: str = fields.CharField(
        description="Подзаголовок в модальном окне",
        max_length=255,
        null=True,
    )

    event_participant_list: fields.ReverseRelation["EventParticipantList"]

    class Meta:
        table = "event_list"


class EventListRepo(BaseEventListRepo, CRUDMixin):
    """
    Репозиторий списка мероприятий.
    """

    model = EventList
