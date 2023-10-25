from tortoise import Model, fields

from common.orm.mixins import CRUDMixin
from src.events_list.entities import BaseEventListRepo


class EventParticipantList(Model):
    """
    Список участников мероприятия.
    """
    id: int = fields.IntField(description="ID", pk=True)
    phone: str = fields.CharField(
        description="Номер телефона пользователя",
        max_length=36,
        null=True,
    )
    event: fields.ForeignKeyNullableRelation = fields.ForeignKeyField(
        model_name="models.EventList",
        null=True,
        description="Название мероприятия",
        related_name="event_participant_list",
        on_delete=fields.SET_NULL,
    )
    code: str = fields.CharField(
        description="Код для QR кода",
        max_length=255,
        null=True,
    )
    group_id: int = fields.IntField(description="ID группы", null=True)
    timeslot: str = fields.CharField(
        description="Время проведения мероприятия",
        max_length=255,
        null=True,
    )

    class Meta:
        table = "event_participant_list"


class EventParticipantListRepo(BaseEventListRepo, CRUDMixin):
    """
    Репозиторий участников мероприятия.
    """

    model = EventParticipantList
