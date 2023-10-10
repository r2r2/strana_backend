from common import orm
from common.orm.mixins import GenericMixin
from tortoise import Model, fields

from ..entities import BaseMeetingRepo


class MeetingCreationSource(Model):
    """
    Модель источника создания встречи.
    """
    id: int = fields.IntField(description='ID', pk=True)
    slug: str = fields.CharField(max_length=20, description='Слаг', unique=True)
    label: str = fields.CharField(max_length=40, description='Название источника создания встречи')

    def __repr__(self):
        return self.slug

    class Meta:
        table = "meetings_meeting_creation_source"


class MeetingCreationSourceRepo(BaseMeetingRepo, GenericMixin):
    """
    Репозиторий источника создания встречи.
    """
    model = MeetingCreationSource
    q_builder: orm.QBuilder = orm.QBuilder(MeetingCreationSource)
    c_builder: orm.ConverterBuilder = orm.ConverterBuilder(MeetingCreationSource)
    a_builder: orm.AnnotationBuilder = orm.AnnotationBuilder(MeetingCreationSource)
