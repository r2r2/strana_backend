from tortoise import fields

from common.orm.mixins import ReadWriteMixin
from src.task_management.entities import BaseTaskModel, BaseTaskRepo


class TaskChain(BaseTaskModel):
    """
    Цепочка заданий
    """

    id: int = fields.IntField(description="ID", pk=True)
    name: str = fields.CharField(max_length=100, description="Название цепочки заданий")
    booking_substage: fields.ManyToManyRelation["AmocrmStatus"] = fields.ManyToManyField(
        model_name="models.AmocrmStatus",
        related_name="taskchain_booking_substages",
        through="taskchain_status_through",
        description="Первое задание в цепочке будет создано при достижении сделкой данного статуса",
        null=True,
        on_delete=fields.CASCADE,
        backward_key="task_chain_substage_id",
        forward_key="status_substage_id",
    )
    task_visibility: fields.ManyToManyRelation["AmocrmStatus"] = fields.ManyToManyField(
        model_name="models.AmocrmStatus",
        related_name="taskchain_task_visibilities",
        through="taskchain_taskvisibility_status_through",
        description="Задание будет видно только в данных статусах, в последующих статусах оно будет не видно",
        null=True,
        on_delete=fields.CASCADE,
        backward_key="task_chain_visibility_id",
        forward_key="status_visibility_id",
    )

    task_statuses: fields.ReverseRelation["TaskStatus"]

    def __repr__(self) -> str:
        return self.name

    class Meta:
        table = "task_management_taskchain"


class TaskChainRepo(BaseTaskRepo, ReadWriteMixin):
    """
    Репозиторий цепочки заданий
    """
    model = TaskChain
