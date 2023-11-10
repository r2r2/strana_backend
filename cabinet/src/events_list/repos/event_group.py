from tortoise import Model, fields

from common.orm.mixins import CRUDMixin
from src.events_list.entities import BaseEventListRepo


class EventGroup(Model):
    """
    Группы мероприятий.
    """
    id: int = fields.IntField(description="ID", pk=True)
    group_id: int = fields.IntField(description="ID группы", null=True)
    timeslot: str = fields.CharField(
        description="Время проведения мероприятия",
        max_length=24,
        null=True,
    )
    event: fields.ForeignKeyNullableRelation["EventList"] = fields.ForeignKeyField(
        model_name="models.EventList",
        null=True,
        description="Мероприятие",
        related_name="groups",
        on_delete=fields.CASCADE,
    )

    qrcode_sms: fields.ManyToManyRelation["QRcodeSMSNotify"]

    class Meta:
        table = "event_groups"


class EventGroupRepo(BaseEventListRepo, CRUDMixin):
    """
    Репозиторий группы.
    """

    model = EventGroup
