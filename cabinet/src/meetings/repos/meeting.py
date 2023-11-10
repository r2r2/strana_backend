from typing import Optional
from datetime import datetime

from tortoise import fields

from common import cfields, orm
from common.orm.mixins import CRUDMixin, CountMixin
from ..entities import BaseMeetingDatabaseModel, BaseMeetingRepo
from ..constants import MeetingType, MeetingPropertyType, MeetingTopicType


class Meeting(BaseMeetingDatabaseModel):
    """
    Встреча
    """
    id: int = fields.IntField(description='ID', pk=True)
    city: fields.ForeignKeyNullableRelation["City"] = fields.ForeignKeyField(
        description="Город",
        model_name="models.City",
        related_name="meeting_city",
        on_delete=fields.SET_NULL,
        null=True,
    )
    project: fields.ForeignKeyNullableRelation["Project"] = fields.ForeignKeyField(
        description="Проект",
        model_name="models.Project",
        related_name="meeting_project",
        on_delete=fields.SET_NULL,
        null=True,
    )
    booking: fields.ForeignKeyNullableRelation['Booking'] = fields.ForeignKeyField(
        description="Сделка",
        model_name="models.Booking",
        related_name="meeting_booking",
        on_delete=fields.SET_NULL,
        null=True,
    )
    status: fields.ForeignKeyNullableRelation['MeetingStatus'] = fields.ForeignKeyField(
        description="Статус встречи",
        model_name="models.MeetingStatus",
        related_name="meetings",
        on_delete=fields.SET_NULL,
        null=True,
    )
    creation_source: fields.ForeignKeyNullableRelation['MeetingCreationSource'] = fields.ForeignKeyField(
        description="Источник создания встречи",
        model_name="models.MeetingCreationSource",
        related_name="meetings",
        on_delete=fields.SET_NULL,
        null=True,
    )
    record_link: Optional[str] = fields.CharField(max_length=255, description="Ссылка на запись", null=True)
    meeting_link: Optional[str] = fields.CharField(max_length=255, description="Ссылка на встречу", null=True)
    meeting_address: Optional[str] = fields.CharField(max_length=300, description="Адрес встречи", null=True)
    topic: str = cfields.CharChoiceField(
        max_length=20, choice_class=MeetingTopicType, default=MeetingTopicType.BUY, description="Тема встречи"
    )
    type: Optional[str] = cfields.CharChoiceField(
        max_length=20, choice_class=MeetingType, default=MeetingType.ONLINE, description="Тип встречи"
    )
    property_type: str = cfields.CharChoiceField(
        max_length=20, choice_class=MeetingPropertyType, default=MeetingPropertyType.FLAT, description="Тип помещения"
    )
    date: datetime = fields.DatetimeField(description="Дата")

    def __str__(self):
        return self.topic

    class Meta:
        table = "meetings_meeting"


class MeetingRepo(BaseMeetingRepo, CRUDMixin, CountMixin):
    """
    Репозиторий встречи
    """
    model = Meeting
    q_builder: orm.QBuilder = orm.QBuilder(Meeting)
