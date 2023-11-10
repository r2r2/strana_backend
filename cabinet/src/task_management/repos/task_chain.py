from typing import Optional

from tortoise import fields, Model

from common.orm.mixins import ReadWriteMixin
from src.task_management.entities import BaseTaskModel, BaseTaskRepo


class TaskChain(BaseTaskModel):
    """
    Цепочка заданий
    """

    id: int = fields.IntField(description="ID", pk=True)
    name: str = fields.CharField(max_length=100, description="Название цепочки заданий")
    sensei_pid: Optional[int] = fields.IntField(description="ID процесса в Sensei", null=True)
    booking_substage: fields.ManyToManyRelation["AmocrmStatus"] = fields.ManyToManyField(
        model_name="models.AmocrmStatus",
        related_name="taskchain_booking_substages",
        through="taskchain_status_through",
        description="Первое задание в цепочке будет создано при достижении сделкой данного статуса",
        null=True,
        on_delete=fields.CASCADE,
        backward_key="task_chain_substage_id",
        forward_key="status_substage_id",
    )
    task_visibility: fields.ManyToManyRelation["AmocrmStatus"] = fields.ManyToManyField(
        model_name="models.AmocrmStatus",
        related_name="taskchain_task_visibilities",
        through="taskchain_taskvisibility_status_through",
        description="Задание будет видно только в данных статусах, в последующих статусах оно будет не видно",
        null=True,
        on_delete=fields.CASCADE,
        backward_key="task_chain_visibility_id",
        forward_key="status_visibility_id",
    )
    task_fields: fields.ManyToManyRelation["TaskFields"] = fields.ManyToManyField(
        model_name="models.TaskField",
        related_name="taskchains",
        through="taskchain_taskfields_through",
        description="Поля задания",
        null=True,
        on_delete=fields.CASCADE,
        backward_key="task_chain_field_id",
        forward_key="task_field_id",
    )
    booking_source: fields.ManyToManyRelation["BookingSource"] = fields.ManyToManyField(
        model_name="models.BookingSource",
        related_name="taskchains",
        through="taskchain_booking_source_through",
        description="Задачи из данной цепочки будут создаваться у данных типов сделок",
        null=True,
        on_delete=fields.SET_NULL,
        backward_key="task_chain_id",
        forward_key="booking_source_id",
    )
    interchangeable_chains: fields.ManyToManyRelation["TaskChain"] = fields.ManyToManyField(
        model_name="models.TaskChain",
        related_name="taskchain_interchangeable_chains",
        through="taskchain_interchangeable_through",
        description="Взаимозаменяемые цепочки заданий",
        null=True,
        on_delete=fields.SET_NULL,
        backward_key="task_chain_id",
        forward_key="interchangeable_chain_id",
    )
    systems: fields.ManyToManyRelation["SystemList"] = fields.ManyToManyField(
        model_name="models.SystemList",
        related_name="taskchains",
        through="taskchain_systems_through",
        description="Список систем",
        null=True,
        on_delete=fields.SET_NULL,
        backward_key="task_chain_id",
        forward_key="system_id",
    )

    task_statuses: fields.ReverseRelation["TaskStatus"]
    task_group_statuses: fields.ReverseRelation["TaskGroupStatus"]

    taskchain_interchangeable_chains: fields.ManyToManyRelation["TaskChain"]

    def __str__(self) -> str:
        return self.name

    class Meta:
        table = "task_management_taskchain"


class TaskChainRepo(BaseTaskRepo, ReadWriteMixin):
    """
    Репозиторий цепочки заданий
    """
    model = TaskChain


class TaskChainBookingSourceThrough(Model):
    """
    Связующая таблица цепочки заданий и источника бронирования
    """
    id: int = fields.IntField(description="ID", pk=True)
    task_chain: fields.ForeignKeyRelation[TaskChain] = fields.ForeignKeyField(
        model_name="models.TaskChain",
        related_name="taskchain_booking_source_through",
        description="Цепочка заданий",
        on_delete=fields.CASCADE,
        backward_key="task_chain_id",
    )
    booking_source: fields.ForeignKeyRelation["BookingSource"] = fields.ForeignKeyField(
        model_name="models.BookingSource",
        related_name="taskchain_booking_source_through",
        description="Источник бронирования",
        on_delete=fields.CASCADE,
        backward_key="booking_source_id",
    )

    class Meta:
        table = "taskchain_booking_source_through"


class TaskChainInterchangeableThrough(Model):
    """
    Связующая таблица цепочки заданий и взаимозаменяемых цепочек
    """
    id: int = fields.IntField(description="ID", pk=True)
    task_chain: fields.ForeignKeyRelation[TaskChain] = fields.ForeignKeyField(
        model_name="models.TaskChain",
        related_name="taskchain_through",
        description="Цепочка заданий",
        on_delete=fields.CASCADE,
        backward_key="task_chain_id",
    )
    interchangeable_chain: fields.ForeignKeyRelation[TaskChain] = fields.ForeignKeyField(
        model_name="models.TaskChain",
        related_name="taskchain_interchangeable_through",
        description="Взаимозаменяемая цепочка заданий",
        on_delete=fields.CASCADE,
        backward_key="interchangeable_chain_id",
    )

    class Meta:
        table = "taskchain_interchangeable_through"


class TaskChainSystemsThrough(Model):
    """
    Связующая таблица цепочки заданий и систем
    """
    id: int = fields.IntField(description="ID", pk=True)
    task_chain: fields.ForeignKeyRelation[TaskChain] = fields.ForeignKeyField(
        model_name="models.TaskChain",
        related_name="taskchain_systems_through",
        description="Цепочка заданий",
        on_delete=fields.CASCADE,
        backward_key="task_chain_id",
    )
    system: fields.ForeignKeyRelation["SystemList"] = fields.ForeignKeyField(
        model_name="models.SystemList",
        related_name="taskchain_systems_through",
        description="Система",
        on_delete=fields.CASCADE,
        backward_key="system_id",
    )

    class Meta:
        table = "taskchain_systems_through"
