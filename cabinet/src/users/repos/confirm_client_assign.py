from datetime import datetime

from tortoise import Model, fields

from common.orm.mixins import CRUDMixin
from src.users.entities import BaseUserRepo


class ConfirmClientAssign(Model):
    """
    Модель подтверждения закрепления клиента за агентом
    """
    id: int = fields.IntField(pk=True, description="ID")
    agent: fields.ForeignKeyNullableRelation["User"] = fields.ForeignKeyField(
        "models.User",
        related_name="agent_confirm_client_assign",
        description="Агент",
        null=True,
        on_delete=fields.SET_NULL,
    )
    client: fields.ForeignKeyNullableRelation["User"] = fields.ForeignKeyField(
        "models.User",
        related_name="client_confirm_client_assign",
        description="Клиент",
        null=True,
        on_delete=fields.SET_NULL,
        index=True,
    )
    agency: fields.ForeignKeyNullableRelation["Agency"] = fields.ForeignKeyField(
        "models.Agency",
        related_name="agency_confirm_client_assign",
        description="Агентство",
        null=True,
        on_delete=fields.SET_NULL,
    )
    assigned_at: datetime = fields.DatetimeField(description="Дата и время закрепления", auto_now_add=True)
    assign_confirmed_at: datetime = fields.DatetimeField(
        description="Дата и время подтверждения закрепления", null=True
    )
    unassigned_at: datetime = fields.DatetimeField(description="Дата и время отказа от агента", null=True)
    comment: str = fields.TextField(description="Комментарий", null=True)

    def __str__(self):
        return f"{self.client} закреплен за {self.agent}"

    class Meta:
        table = "users_confirm_client_assign"


class ConfirmClientAssignRepo(BaseUserRepo, CRUDMixin):
    """
    Репозиторий для работы с моделью ConfirmClientAssign
    """
    model = ConfirmClientAssign
