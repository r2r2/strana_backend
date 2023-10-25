from typing import Optional

from pydantic import root_validator

from src.task_management.constants import ButtonCondition
from src.task_management.entities import BaseTaskSchema, BaseTaskCamelCaseSchema


class TaskInstanceUpdateSchema(BaseTaskSchema):
    """
    Схема обновления экземпляра задания
    """
    comment: Optional[str]
    task_amocrmid: Optional[str]
    slug: str

    class Config:
        orm_mode = True


class ButtonActionSchema(BaseTaskCamelCaseSchema):
    type: str
    id: str
    condition: ButtonCondition.serializer | None

    @root_validator
    def validate_condition(cls, values):
        if condition := values.get("condition"):
            values["condition"] = condition.value
        else:
            values.pop("condition")
        return values

    class Config:
        orm_mode = True


class ButtonSchema(BaseTaskCamelCaseSchema):
    """
    Схема кнопки
    """
    label: str
    type: str
    slug_step: str | None
    action: ButtonActionSchema

    class Config:
        orm_mode = True


class UpdateTaskResponseSchema(BaseTaskCamelCaseSchema):
    """
    Схема ответа об обновлении экземпляра задания
    """
    id: int
    type: str
    title: str
    hint: str | None
    text: str
    current_step: str | None
    task_status: str
    buttons: list[ButtonSchema] | None
    buttons_detail_view: list[ButtonSchema] | None

    class Config:
        orm_mode = True


class GetTaskResponseSchema(UpdateTaskResponseSchema):
    """
    Схема ответа о получении экземпляра задания
    """

    class Config:
        orm_mode = True
