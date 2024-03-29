from tortoise import fields

from common import cfields
from common.orm.mixins import ReadWriteMixin
from src.task_management.constants import ButtonStyle
from src.task_management.entities import BaseTaskModel, BaseTaskRepo


class Button(BaseTaskModel):
    styles = ButtonStyle()

    id: int = fields.IntField(description="ID", pk=True)
    label: str = fields.CharField(max_length=100, description="Название кнопки")
    style: str = cfields.CharChoiceField(
        choice_class=ButtonStyle,
        description="Стиль кнопки",
        max_length=20,
    )
    slug: str = fields.CharField(max_length=100, description="Слаг кнопки")
    priority: int = fields.IntField(
        description="Чем меньше приоритет - тем выше выводится кнопка в интерфейсе задания",
        null=True
    )
    statuses: fields.ManyToManyRelation["TaskStatus"] = fields.ManyToManyField(
        model_name="models.TaskStatus",
        related_name="buttons",
        through="task_management_taskstatus_buttons",
        description="Статусы задачи, к которым привязана кнопка",
        null=True,
        on_delete=fields.CASCADE,
        backward_key="button_id",
        forward_key="task_status_id",
    )

    def __repr__(self) -> str:
        return self.label

    class Meta:
        table = "task_management_button"


class TaskStatusButtonsThrough(BaseTaskModel):
    id: int = fields.IntField(description="ID", pk=True)
    button: fields.ForeignKeyRelation[Button] = fields.ForeignKeyField(
        model_name="models.Button",
        related_name="task_status_buttons_through",
        on_delete=fields.CASCADE,
        description="Кнопка",
    )
    task_status: fields.ForeignKeyRelation["TaskStatus"] = fields.ForeignKeyField(
        model_name="models.TaskStatus",
        related_name="task_status_buttons_through",
        on_delete=fields.CASCADE,
        description="Статус задачи",
    )

    class Meta:
        table = "task_management_taskstatus_buttons"


class ButtonRepo(BaseTaskRepo, ReadWriteMixin):
    model = Button
