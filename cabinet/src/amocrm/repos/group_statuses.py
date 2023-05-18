from common import orm
from common.orm.mixins import GenericMixin
from tortoise import Model, fields

from ..entities import BaseAmocrmRepo


class AmocrmGroupStatus(Model):
    """
    Модель Группирующих статусов
    """
    id: int = fields.IntField(description='ID', pk=True)
    name: str = fields.CharField(max_length=150, description='Имя группирующего статуса', null=True)
    sort: int = fields.IntField(description='Приоритет', default=0)

    statuses: fields.ReverseRelation["AmocrmStatus"]

    def __repr__(self):
        return self.name

    class Meta:
        table = "amocrm_group_statuses"


class AmocrmGroupStatusRepo(BaseAmocrmRepo, GenericMixin):
    """
    Репозиторий Группирующих статусов
    """
    model = AmocrmGroupStatus
    q_builder: orm.QBuilder = orm.QBuilder(AmocrmGroupStatus)
    c_builder: orm.ConverterBuilder = orm.ConverterBuilder(AmocrmGroupStatus)
    a_builder: orm.AnnotationBuilder = orm.AnnotationBuilder(AmocrmGroupStatus)
