from typing import Any

from pydantic import root_validator, parse_obj_as

from src.task_management.constants import TaskStatusType
from src.task_management.entities import BaseTaskCamelCaseSchema
from src.task_management.repos import TaskStatus


class TaskChainSchema(BaseTaskCamelCaseSchema):
    """
    Схема цепочки заданий
    """
    name: str


class TaskStatusSchema(BaseTaskCamelCaseSchema):
    """
    Схема статуса задачи
    """
    name: str
    description: str
    type: TaskStatusType.serializer
    priority: int
    slug: str


class TaskChainStatusesResponseSchema(BaseTaskCamelCaseSchema):
    """
    Схема статусов цепочки заданий
    """
    name: str
    priority: int
    color: str | None
    slug: str
    task_chain: TaskChainSchema
    statuses: Any

    @root_validator
    def validate_statuses(cls, values):
        if statuses := values.get('statuses'):
            statuses: list[TaskStatus] = [status for status in statuses]
            values['statuses'] = parse_obj_as(list[TaskStatusSchema], statuses)
        return values

