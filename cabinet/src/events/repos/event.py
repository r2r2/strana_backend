from datetime import date
from typing import Optional, Any
from common import cfields, mixins, orm
from common.orm.mixins import CRUDMixin
from tortoise import Model, fields

from ..entities import BaseEventRepo


class EventType(mixins.Choices):
    """
    Тип мероприятия.
    """
    ONLINE: tuple[str] = "online", "Онлайн"
    OFFLINE: tuple[str] = "offline", "Офлайн"


class Event(Model):
    """
    Мероприятие.
    """

    id: int = fields.IntField(description="ID", pk=True, index=True)
    name: str = fields.CharField(
        description="Название мероприятия",
        max_length=100,
    )
    description: Optional[str] = fields.TextField(
        description="Описание мероприятия",
        null=True,
    )
    comment: Optional[str] = fields.TextField(
        description="Комментарий",
        null=True,
    )
    type: Optional[str] = cfields.CharChoiceField(
        description="Тип мероприятия",
        max_length=10,
        choice_class=EventType,
        null=True,
    )
    city: Optional[fields.ForeignKeyNullableRelation["City"]] = fields.ForeignKeyField(
        description="Город мероприятия (офлайн)",
        model_name="models.City",
        related_name="event_city",
        on_delete=fields.SET_NULL,
        null=True,
    )
    address: Optional[str] = fields.TextField(
        description="Адрес мероприятия (офлайн)",
        null=True,
    )
    link: Optional[str] = fields.TextField(
        description="Ссылка на мероприятие (онлайн)",
        null=True,
    )
    meeting_date_start: date = fields.DatetimeField(
        description="Дата и время начала мероприятия",
    )
    meeting_date_end: date = fields.DatetimeField(
        description="Дата и время окончания мероприятия",
        null=True,
    )
    record_date_end: date = fields.DatetimeField(
        description="Дата и время окончания записи на мероприятие",
        null=True,
    )
    manager_fio: str = fields.TextField(description="ФИО ответственного менеджера")
    manager_phone: str = fields.CharField(
        description="Номер телефона ответственного менеджера",
        max_length=20,
        index=True,
    )
    max_participants_number: int = fields.IntField(description="Макс. количество участников мероприятия", default=0)
    image: Optional[dict[str, Any]] = cfields.MediaField(
        description="Фото мероприятия",
        max_length=500,
        null=True,
    )
    show_in_all_cities: bool = fields.BooleanField(
        description="Показывать во всех городах",
        default=True,
    )
    is_active: bool = fields.BooleanField(
        description="Мепроприятие активно",
        default=True,
    )
    tags: fields.ManyToManyRelation["EventTag"] = fields.ManyToManyField(
        description="Теги мероприятий",
        model_name="models.EventTag",
        related_name="events",
        on_delete=fields.SET_NULL,
        through="event_event_tag_and_event",
        backward_key="event_id",
        forward_key="tag_id",
        null=True,
    )

    def __repr__(self):
        return self.name

    class Meta:
        table = "event_event"


class EventRepo(BaseEventRepo, CRUDMixin):
    """
    Репозиторий мероприятия.
    """
    model = Event
    q_builder: orm.QBuilder = orm.QBuilder(Event)
    c_builder: orm.ConverterBuilder = orm.ConverterBuilder(Event)
    a_builder: orm.AnnotationBuilder = orm.AnnotationBuilder(Event)
