from tortoise import fields

from common import cfields
from common.orm.mixins import ReadWriteMixin
from src.task_management.constants import TaskStatusType
from src.task_management.entities import BaseTaskModel, BaseTaskRepo


class TaskStatus(BaseTaskModel):
    """
    Статус задачи
    """
    types = TaskStatusType()

    id: int = fields.IntField(description="ID", pk=True)
    name: str = fields.CharField(max_length=100, description="Выводится в списке сущностей и в карточке сущности")
    description: str = fields.TextField(description="Выводится в карточке сущности.")
    type: str = cfields.CharChoiceField(
        choice_class=TaskStatusType,
        description="Влияет на выводимую иконку",
        max_length=20,
    )
    priority: int = fields.IntField(
        description="Чем больше приоритет, тем выше будет выводиться задание в карточке (если заданий несколько)",
    )
    slug: str = fields.CharField(max_length=255, description="Символьный код")

    tasks_chain: fields.ForeignKeyRelation["TaskChain"] = fields.ForeignKeyField(
        model_name="models.TaskChain",
        related_name="task_statuses",
        on_delete=fields.CASCADE,
        description="Определяет триггер запуска первого задания в цепочке (задается в цепочке заданий). "
                    "Логика переходов заданий по цепочке зашита в коде.",
    )

    task_instances: fields.ReverseRelation["TaskInstance"]
    button: fields.ReverseRelation["Button"]

    def __str__(self) -> str:
        return self.name

    class Meta:
        table = "task_management_taskstatus"


class TaskStatusRepo(BaseTaskRepo, ReadWriteMixin):
    """
    Репозиторий статуса задачи
    """
    model = TaskStatus
