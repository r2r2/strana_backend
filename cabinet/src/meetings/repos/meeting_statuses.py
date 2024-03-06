from common import orm
from common.orm.mixins import GenericMixin
from tortoise import Model, fields

from ..entities import BaseMeetingRepo


# deprecated
class MeetingStatus(Model):
    """
    Модель статуса встречи.
    """
    id: int = fields.IntField(description='ID', pk=True)
    sort: int = fields.IntField(default=0, description='Сортировка')
    slug: str = fields.CharField(max_length=20, description='Слаг', unique=True)
    label: str = fields.CharField(max_length=40, description='Название статуса встречи')
    is_final: bool = fields.BooleanField(description="Завершающий статус", default=False)

    def __repr__(self):
        return self.slug

    class Meta:
        table = "meetings_status_meeting"
        ordering = ["sort"]


class MeetingStatusRef(Model):
    """
    Модель статуса встречи.
    """
    slug: str = fields.CharField(max_length=20, description='Слаг', pk=True)
    sort: int = fields.IntField(default=0, description='Сортировка')
    label: str = fields.CharField(max_length=40, description='Название статуса встречи')
    is_final: bool = fields.BooleanField(description="Завершающий статус", default=False)

    def __repr__(self):
        return self.slug

    class Meta:
        table = "meetings_status_meeting_ref"
        ordering = ["sort"]


class MeetingStatusRepo(BaseMeetingRepo, GenericMixin):
    """
    Репозиторий статусов встречи.
    """
    model = MeetingStatus
    q_builder: orm.QBuilder = orm.QBuilder(MeetingStatus)
    c_builder: orm.ConverterBuilder = orm.ConverterBuilder(MeetingStatus)
    a_builder: orm.AnnotationBuilder = orm.AnnotationBuilder(MeetingStatus)


class MeetingStatusRefRepo(BaseMeetingRepo, GenericMixin):
    """
    Репозиторий статусов встречи.
    """
    model = MeetingStatusRef
    q_builder: orm.QBuilder = orm.QBuilder(MeetingStatusRef)
    c_builder: orm.ConverterBuilder = orm.ConverterBuilder(MeetingStatusRef)
    a_builder: orm.AnnotationBuilder = orm.AnnotationBuilder(MeetingStatusRef)
