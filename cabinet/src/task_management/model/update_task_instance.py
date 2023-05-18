from typing import Optional

from src.task_management.entities import BaseTaskSchema


class TaskInstanceUpdateSchema(BaseTaskSchema):
    """
    Схема обновления экземпляра задания
    """
    comment: Optional[str]
    task_amocrmid: Optional[str]
    slug: str

    class Config:
        orm_mode = True
