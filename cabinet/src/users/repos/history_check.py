from datetime import date
from typing import Optional

from tortoise import Model, fields
from tortoise.fields import ForeignKeyNullableRelation

from common import cfields, orm
from common.orm.mixins import GenericMixin
from src.agencies.repos import Agency
from .user import User
from ..constants import UserStatusCheck
from ..entities import BaseUserRepo


class CheckHistory(Model):
    """
    История проверки
    """

    id: int = fields.BigIntField(description="ID", pk=True)
    agent: ForeignKeyNullableRelation[User] = fields.ForeignKeyField(
        description="Агент",
        model_name="models.User",
        on_delete=fields.SET_NULL,
        related_name="agent_history_check",
        null=True,
    )
    client: ForeignKeyNullableRelation[User] = fields.ForeignKeyField(
        description="Клиент",
        model_name="models.User",
        on_delete=fields.SET_NULL,
        related_name="users_history_check",
        null=True,
    )
    client_phone: Optional[str] = fields.CharField(
        description="Номер телефона клиента", max_length=20, null=True, index=True
    )
    agency: ForeignKeyNullableRelation[Agency] = fields.ForeignKeyField(
        description="Агентство",
        model_name="models.Agency",
        on_delete=fields.SET_NULL,
        related_name="agencies_history_check",
        null=True,
    )
    status: Optional[str] = cfields.CharChoiceField(
        description="Статус проверки", max_length=20, choice_class=UserStatusCheck, null=True, index=True
    )
    created_at: Optional[date] = fields.DatetimeField(description="Дата проверки", auto_now_add=True)

    class Meta:
        table = "users_checks_history"


class CheckHistoryRepo(BaseUserRepo, GenericMixin):
    """
    Репозиторий истории проверки
    """
    model = CheckHistory
    q_builder: orm.QBuilder = orm.QBuilder(CheckHistory)
