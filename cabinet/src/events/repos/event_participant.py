from common import cfields, mixins, orm
from common.orm.mixins import CRUDMixin
from src.users.repos import User
from tortoise import Model, fields
from tortoise.fields import ForeignKeyNullableRelation

from ..entities import BaseEventRepo


class EventParticipantStatus(mixins.Choices):
    """
    Статус участника мероприятия.
    """

    RECORDED: tuple[str] = "recorded", "Записан"
    REFUSED: tuple[str] = "refused", "Отказался"


class EventParticipant(Model):
    """
    Участник мероприятия.
    """

    id: int = fields.IntField(description="ID", pk=True, index=True)
    fio: str = fields.TextField(description="ФИО агента участника")
    phone: str = fields.CharField(
        description="Номер телефона агента участника",
        max_length=20,
        index=True,
    )
    agent: ForeignKeyNullableRelation[User] = fields.ForeignKeyField(
        description="Агент участник",
        model_name="models.User",
        related_name="participants",
        on_delete=fields.CASCADE,
    )
    status: str = cfields.CharChoiceField(
        description="Статус агента участника",
        max_length=10,
        choice_class=EventParticipantStatus,
        default=EventParticipantStatus.RECORDED,
    )
    event: fields.ForeignKeyNullableRelation["Event"] = fields.ForeignKeyField(
        description="Мероприятие",
        model_name="models.Event",
        related_name="participants",
        on_delete=fields.CASCADE,
    )

    def __repr__(self):
        return self.fio

    class Meta:
        table = "event_event_participant"


class EventParticipantRepo(BaseEventRepo, CRUDMixin):
    """
    Репозиторий участника мероприятия.
    """
    model = EventParticipant
    q_builder: orm.QBuilder = orm.QBuilder(EventParticipant)
    c_builder: orm.ConverterBuilder = orm.ConverterBuilder(EventParticipant)
    a_builder: orm.AnnotationBuilder = orm.AnnotationBuilder(EventParticipant)
