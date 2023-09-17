from src.task_management.constants import TaskStatusType
from src.task_management.entities import BaseTaskSchema


class TaskChainStatusesResponseSchema(BaseTaskSchema):
    """
    Схема статусов цепочки заданий
    """
    name: str
    description: str
    type: TaskStatusType.serializer
    priority: int
    slug: str

    class Config:
        orm_mode = True
