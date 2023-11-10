from datetime import date

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
    event_id: int = fields.IntField(description="ID мероприятия", null=True)
    event_date: date = fields.DateField(
        description="Дата мероприятия",
        null=True,
    )
    start_showing_date: date = fields.DateField(
        description="Дата начала показа мероприятия",
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
    text: str = fields.TextField(
        description="Текст в модальном окне",
        null=True,
        default="QR-код активен 1 раз после прохода, пересылка третьим лицам запрещена",
    )

    event_participant_list: fields.ReverseRelation["EventParticipantList"]
    groups: fields.ReverseRelation["EventGroup"]

    qrcode_sms: fields.ManyToManyRelation["QRcodeSMSNotify"]

    class Meta:
        table = "event_list"


class EventListRepo(BaseEventListRepo, CRUDMixin):
    """
    Репозиторий списка мероприятий.
    """

    model = EventList
