from typing import Optional

from tortoise import fields

from common import orm
from common.orm.mixins import ReadWriteMixin
from src.task_management.entities import BaseTaskModel, BaseTaskRepo


class TaskInstance(BaseTaskModel):
    """
    Задача
    """

    id: int = fields.IntField(description="ID", pk=True)
    comment: str = fields.TextField(description="Комментарий администратора АМО", null=True)
    task_amocrmid: Optional[str] = fields.CharField(max_length=255, description="ID задачи в АМО", null=True)
    sensei_pid: Optional[int] = fields.IntField(description="ID процесса в Sensei", null=True)
    status: fields.ForeignKeyRelation["TaskStatus"] = fields.ForeignKeyField(
        model_name="models.TaskStatus",
        related_name="task_instances",
        on_delete=fields.CASCADE,
        description="Логика переходов заданий между шаблонами зашита и описана в проектной документации."
    )
    booking: fields.ForeignKeyRelation["Booking"] = fields.ForeignKeyField(
        model_name="models.Booking",
        related_name="task_instances",
        on_delete=fields.CASCADE,
        description="ID сущности, в которой будет выводиться задание",
    )

    def __repr__(self) -> str:
        return f"TaskInstance id: {self.id}"

    class Meta:
        table = "task_management_taskinstance"


class TaskInstanceRepo(BaseTaskRepo, ReadWriteMixin):
    """
    Репозиторий задачи
    """
    model = TaskInstance
    q_builder: orm.QBuilder = orm.QBuilder(TaskInstance)
    c_builder: orm.ConverterBuilder = orm.ConverterBuilder(TaskInstance)
    a_builder: orm.AnnotationBuilder = orm.AnnotationBuilder(TaskInstance)
