from datetime import date
from typing import Any, Optional

from common import cfields, mixins, orm
from common.orm.mixins import CRUDMixin
from src.meetings.repos import Meeting
from tortoise import Model, fields
from tortoise.fields import ForeignKeyNullableRelation

from ..entities import BaseEventRepo
from . import Event


class CalendarEventType(mixins.Choices):
    """
    Тип события календаря.
    """
    EVENT: tuple[str] = "event", "Мероприятие"
    MEETING: tuple[str] = "meeting", "Встреча"


class CalendarEventFormatType(mixins.Choices):
    """
    Тип формата события календаря.
    """
    ONLINE: tuple[str] = "online", "Онлайн"
    OFFLINE: tuple[str] = "offline", "Офлайн"


class CalendarEvent(Model):
    """
    Событие календаря.
    """

    id: int = fields.IntField(description="ID", pk=True, index=True)
    title: str = fields.CharField(
        description="Название события календаря",
        max_length=100,
        null=True,
    )
    type: Optional[str] = cfields.CharChoiceField(
        description="Тип события календаря",
        max_length=10,
        choice_class=CalendarEventType,
    )
    format_type: Optional[str] = cfields.CharChoiceField(
        description="Тип формата события календаря",
        max_length=10,
        choice_class=CalendarEventFormatType,
    )
    date_start: date = fields.DatetimeField(
        description="Дата и время начала события календаря",
    )
    date_end: date = fields.DatetimeField(
        description="Дата и время окончания события календаря",
        null=True,
    )
    event: ForeignKeyNullableRelation[Event] = fields.OneToOneField(
        description="Мероприятие",
        model_name="models.Event",
        on_delete=fields.CASCADE,
        related_name="calendar_event",
        null=True,
    )
    meeting: ForeignKeyNullableRelation[Meeting] = fields.OneToOneField(
        description="Мероприятие",
        model_name="models.Meeting",
        on_delete=fields.CASCADE,
        related_name="calendar_event",
        null=True,
    )
    tags: fields.ManyToManyRelation["EventTag"] = fields.ManyToManyField(
        description="Теги событий календаря",
        model_name="models.EventTag",
        related_name="calendar_events",
        on_delete=fields.SET_NULL,
        through="event_event_tag_and_calendar_event",
        backward_key="calendar_event_id",
        forward_key="tag_id",
        null=True,
    )

    def __repr__(self):
        return self.title

    class Meta:
        table = "event_calendar_event"


class CalendarEventRepo(BaseEventRepo, CRUDMixin):
    """
    Репозиторий мероприятия.
    """
    model = CalendarEvent
    q_builder: orm.QBuilder = orm.QBuilder(CalendarEvent)
    c_builder: orm.ConverterBuilder = orm.ConverterBuilder(CalendarEvent)
    a_builder: orm.AnnotationBuilder = orm.AnnotationBuilder(CalendarEvent)


class CalendarEventTypeSettings(Model):
    """
    Настройки типов событий календаря.
    """

    id: int = fields.IntField(description="ID", pk=True, index=True)
    type: Optional[str] = cfields.CharChoiceField(
        description="Тип события календаря",
        max_length=10,
        choice_class=CalendarEventType,
        unique=True,
    )
    color: str = fields.CharField(
        max_length=40,
        description='Цвет типа события календаря',
        default="#808080",
    )

    def __repr__(self):
        return self.color

    class Meta:
        table = "event_calendar_event_type_settings"


class CalendarEventTypeSettingsRepo(BaseEventRepo, CRUDMixin):
    """
    Репозиторий настроек типов событий календаря.
    """
    model = CalendarEventTypeSettings
    q_builder: orm.QBuilder = orm.QBuilder(CalendarEventTypeSettings)
    c_builder: orm.ConverterBuilder = orm.ConverterBuilder(CalendarEventTypeSettings)
    a_builder: orm.AnnotationBuilder = orm.AnnotationBuilder(CalendarEventTypeSettings)
