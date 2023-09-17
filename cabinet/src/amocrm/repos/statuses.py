from common import orm
from common.orm.mixins import GenericMixin
from tortoise import Model, fields

from ..entities import BaseAmocrmRepo


class AmocrmStatus(Model):
    """
    Модель Статуса
    """
    id: int = fields.IntField(description='ID', pk=True)
    name: str = fields.CharField(max_length=150, description='Имя сделки', null=True)
    sort: int = fields.IntField(default=0, description='Сортировка')
    pipeline: fields.ForeignKeyRelation = fields.ForeignKeyField(
        model_name="models.AmocrmPipeline", related_name='statuses', on_delete=fields.CASCADE
    )
    group_status: fields.ForeignKeyRelation = fields.ForeignKeyField(
        model_name="models.AmocrmGroupStatus", related_name='statuses', null=True, on_delete=fields.SET_NULL
    )
    client_group_status: fields.ForeignKeyRelation = fields.ForeignKeyField(
        model_name="models.ClientAmocrmGroupStatus", related_name='client_statuses', null=True,
        on_delete=fields.SET_NULL
    )

    taskchain_booking_substages: fields.ManyToManyRelation["TaskChain"]
    taskchain_task_visibilities: fields.ManyToManyRelation["TaskChain"]
    pinning_status_statuses: fields.ManyToManyRelation["PinningStatus"]

    def __repr__(self):
        return self.name

    class Meta:
        table = "amocrm_statuses"


class AmocrmStatusRepo(BaseAmocrmRepo, GenericMixin):
    """
    Репозиторий статусов
    """
    model = AmocrmStatus
    q_builder: orm.QBuilder = orm.QBuilder(AmocrmStatus)
    c_builder: orm.ConverterBuilder = orm.ConverterBuilder(AmocrmStatus)
    a_builder: orm.AnnotationBuilder = orm.AnnotationBuilder(AmocrmStatus)
