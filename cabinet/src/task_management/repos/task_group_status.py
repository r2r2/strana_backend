from tortoise import Model, fields

from common.orm.mixins import CRUDMixin
from src.task_management.entities import BaseTaskRepo


class TaskGroupStatus(Model):
    """
    Группирующие статусы для задач
    """
    id: int = fields.IntField(pk=True)
    name: str = fields.CharField(max_length=255)
    priority: int = fields.IntField(default=0, description="Сортировка")
    color: str = fields.CharField(max_length=16, null=True, description="HEX код цвета")
    slug: str = fields.CharField(max_length=255, description="Слаг группового статуса")
    created_at: fields.DatetimeField = fields.DatetimeField(auto_now_add=True)
    updated_at: fields.DatetimeField = fields.DatetimeField(auto_now=True)

    task_chain: fields.ForeignKeyRelation["TaskChain"] = fields.ForeignKeyField(
        model_name="models.TaskChain",
        related_name="task_group_statuses",
        on_delete=fields.CASCADE,
        description="Цепочка задач",
    )
    statuses: fields.ManyToManyRelation["TaskStatus"] = fields.ManyToManyField(
        "models.TaskStatus",
        related_name="task_group_statuses",
        through="task_management_group_status_through",
        description="Статусы задач",
        null=True,
        on_delete=fields.CASCADE,
        backward_key="task_group_status_id",
        forward_key="task_status_id",
    )

    def __str__(self) -> str:
        return self.name

    class Meta:
        table = "task_management_group_statuses"


class TaskGroupStatusThrough(Model):
    id: int = fields.IntField(description="ID", pk=True)
    task_group_status: fields.ForeignKeyRelation[TaskGroupStatus] = fields.ForeignKeyField(
        model_name="models.TaskGroupStatus",
        related_name="task_group_status_through",
        description="Группа статусов задач",
        on_delete=fields.CASCADE,
        backward_key="task_group_status_id",
    )
    task_status: fields.ForeignKeyRelation["TaskStatus"] = fields.ForeignKeyField(
        model_name="models.TaskStatus",
        related_name="task_group_status_through",
        description="Статус задачи",
        on_delete=fields.CASCADE,
        backward_key="task_status_id",
    )

    def __str__(self) -> str:
        return f"{self.task_group_status} - {self.task_status}"

    class Meta:
        table = "task_management_group_status_through"


class TaskGroupStatusRepo(BaseTaskRepo, CRUDMixin):
    """
    Репозиторий группы статусов задач
    """
    model = TaskGroupStatus
