from tortoise import fields

from common.orm.mixins import ReadWriteMixin
from src.task_management.entities import BaseTaskModel, BaseTaskRepo


class TaskField(BaseTaskModel):
    """
    Поля заданий
    """
    id: int = fields.IntField(description="ID", pk=True)
    name: str = fields.CharField(max_length=100, description="Название поля")
    type: str = fields.CharField(max_length=100, description="Тип поля", null=True)
    field_name: str = fields.CharField(max_length=100, description="Название поля в БД")

    taskchains: fields.ManyToManyRelation["TaskChain"]

    def __str__(self) -> str:
        return self.name

    class Meta:
        table = "task_management_taskfields"


class TaskFieldRepo(BaseTaskRepo, ReadWriteMixin):
    """
    Репозиторий полей заданий
    """
    model = TaskField
