from common import orm
from common.orm.mixins import GenericMixin
from tortoise import Model, fields

from ..entities import BaseAmocrmRepo


class ClientAmocrmGroupStatus(Model):
    """
    Модель Группирующих статусов для клиентов
    """
    id: int = fields.IntField(description='ID', pk=True)
    name: str = fields.CharField(max_length=150, description='Имя группирующего статуса', null=True)
    sort: int = fields.IntField(description='Приоритет', default=0)
    color: str = fields.CharField(max_length=40, description='Цвет', null=True)
    is_final: bool = fields.BooleanField(description="Завершающий статус", default=False)
    is_hide: bool = fields.BooleanField(description="Скрыть статус", default=False)

    show_reservation_date: bool = fields.BooleanField(description="Выводить дату резерва", default=False)
    show_booking_date: bool = fields.BooleanField(description="Выводить дату брони", default=False)

    task_chains: fields.ManyToManyRelation["TaskChain"] = fields.ManyToManyField(
        model_name="models.TaskChain",
        related_name="taskchain_client_group_statuses",
        through="taskchain_client_group_status_through",
        description="Цепочки заданий",
        null=True,
        on_delete=fields.SET_NULL,
        backward_key="client_group_status_id",
        forward_key="task_chain_id",
    )

    booking_tags: fields.ManyToManyRelation["BookingTag"]
    statuses: fields.ReverseRelation["AmocrmStatus"]

    def __repr__(self):
        return self.name

    class Meta:
        table = "client_amocrm_group_statuses"


class TaskChainClientGroupStatusThrough(Model):
    """
    Связь между цепочками заданий и группирующими статусами
    """
    id: int = fields.IntField(description='ID', pk=True)
    task_chain: fields.ForeignKeyRelation["TaskChain"] = fields.ForeignKeyField(
        model_name="models.TaskChain",
        related_name="taskchain_client_group_status_through",
        description="Цепочки заданий",
        null=True,
        on_delete=fields.CASCADE,
        backward_key="task_chain_id",
        forward_key="client_group_status_id",
    )
    client_group_status: fields.ForeignKeyRelation["ClientAmocrmGroupStatus"] = fields.ForeignKeyField(
        model_name="models.ClientAmocrmGroupStatus",
        related_name="taskchain_client_group_status_through",
        description="Группирующие статусы",
        null=True,
        on_delete=fields.CASCADE,
        backward_key="client_group_status_id",
        forward_key="task_chain_id",
    )

    class Meta:
        table = "taskchain_client_group_status_through"


class ClientAmocrmGroupStatusRepo(BaseAmocrmRepo, GenericMixin):
    """
    Репозиторий Группирующих статусов
    """
    model = ClientAmocrmGroupStatus
    q_builder: orm.QBuilder = orm.QBuilder(ClientAmocrmGroupStatus)
    c_builder: orm.ConverterBuilder = orm.ConverterBuilder(ClientAmocrmGroupStatus)
    a_builder: orm.AnnotationBuilder = orm.AnnotationBuilder(ClientAmocrmGroupStatus)
