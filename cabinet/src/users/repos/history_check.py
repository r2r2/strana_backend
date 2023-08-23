from datetime import date
from typing import Optional

from tortoise import Model, fields
from tortoise.fields import ForeignKeyNullableRelation

from common import orm
from common.orm.mixins import GenericMixin
from src.agencies.repos import Agency
from .user import User
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
    unique_status: fields.ForeignKeyNullableRelation["UniqueStatus"] = fields.ForeignKeyField(
        description="Статус уникальности",
        model_name="models.UniqueStatus",
        on_delete=fields.CASCADE,
        related_name="checks_history",
        null=True,
    )
    created_at: Optional[date] = fields.DatetimeField(description="Дата проверки", auto_now_add=True)

    term_uid: Optional[str] = fields.CharField(
        description="UID условия проверки на уникальность",
        max_length=255,
        null=True,
    )
    term_comment: Optional[str] = fields.TextField(
        description="Комментарий к условию проверки на уникальность",
        null=True,
    )
    lead_link: Optional[str] = fields.TextField(
        description="Ссылка на сделку",
        null=True,
    )


    class Meta:
        table = "users_checks_history"


class CheckHistoryRepo(BaseUserRepo, GenericMixin):
    """
    Репозиторий истории проверки
    """
    model = CheckHistory
    q_builder: orm.QBuilder = orm.QBuilder(CheckHistory)
