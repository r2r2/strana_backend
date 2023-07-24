from common import orm
from common.orm.mixins import CRUDMixin
from tortoise import Model, fields

from ..entities import BaseEventRepo


class EventTag(Model):
    """
    Теги мероприятий.
    """

    id: int = fields.IntField(description="ID", pk=True, index=True)
    name: str = fields.CharField(
        description="Название тега",
        max_length=100,
        unique=True,
    )
    color: str = fields.CharField(
        max_length=40,
        description='Цвет тега',
        default="#808080",
    )
    text_color: str = fields.CharField(
        max_length=40,
        description='Цвет текста тега',
        default="#808080",
    )

    def __repr__(self):
        return self.name

    class Meta:
        table = "event_event_tag"


class EventTagRepo(BaseEventRepo, CRUDMixin):
    """
    Репозиторий тегов мероприятий.
    """
    model = EventTag
    q_builder: orm.QBuilder = orm.QBuilder(EventTag)
    c_builder: orm.ConverterBuilder = orm.ConverterBuilder(EventTag)
    a_builder: orm.AnnotationBuilder = orm.AnnotationBuilder(EventTag)
