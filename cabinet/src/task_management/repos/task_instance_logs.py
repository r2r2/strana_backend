from tortoise import Model, fields

from common.loggers.repos import AbstractLogMixin
from common.orm.mixins import CreateMixin, ListMixin
from src.task_management.entities import BaseTaskRepo


class TaskInstanceLog(Model, AbstractLogMixin):
    """
    Лог задачи
    """
    task_instance: fields.ForeignKeyNullableRelation["TaskInstance"] = fields.ForeignKeyField(
        description="Экземпляр задания",
        model_name="models.TaskInstance",
        related_name="task_instance_logs",
        null=True,
    )

    def __str__(self) -> str:
        return str(self.id)

    class Meta:
        table = "task_management_logs"


class TaskInstanceLogRepo(BaseTaskRepo, CreateMixin, ListMixin):
    """
    Репозиторий лога задачи
    """
    model = TaskInstanceLog
