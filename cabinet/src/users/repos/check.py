from datetime import datetime
from typing import Optional

from common import cfields, orm
from common.orm.mixins import CRUDMixin
from src.agencies.repos import Agency
from tortoise import Model, fields
from tortoise.fields import ForeignKeyNullableRelation

from ..constants import UserStatus
from ..entities import BaseUserRepo
from .user import User


class Check(Model):
    """
    Проверка
    """

    id: int = fields.BigIntField(description="ID", pk=True)
    requested: Optional[datetime] = fields.DatetimeField(description="Запрошено", null=True)
    dispute_requested: Optional[datetime] = fields.DatetimeField(description="Время оспаривания", null=True)
    status_fixed: bool = fields.BooleanField(description="Закрепить статус за клиентом", default=False)
    status: Optional[str] = cfields.CharChoiceField(
        description="Статус", max_length=20, choice_class=UserStatus, null=True, index=True
    )
    user: ForeignKeyNullableRelation[User] = fields.ForeignKeyField(
        description="Пользователь",
        model_name="models.User",
        on_delete=fields.SET_NULL,
        related_name="users_checks",
        null=True,
    )
    agent: ForeignKeyNullableRelation[User] = fields.ForeignKeyField(
        description="Агент",
        model_name="models.User",
        on_delete=fields.SET_NULL,
        related_name="agents_checks",
        null=True,
    )
    dispute_agent: ForeignKeyNullableRelation[User] = fields.ForeignKeyField(
        description="Оспаривающий агент",
        model_name="models.User",
        on_delete=fields.SET_NULL,
        related_name="dispute_agents_checks",
        null=True,
    )
    agency: ForeignKeyNullableRelation[Agency] = fields.ForeignKeyField(
        description="Агентство",
        model_name="models.Agency",
        on_delete=fields.SET_NULL,
        related_name="agencies_checks",
        null=True,
    )
    admin: ForeignKeyNullableRelation[User] = fields.ForeignKeyField(
        description="Админ",
        model_name="models.User",
        on_delete=fields.SET_NULL,
        related_name="admin_checks",
        null=True,
    )
    comment: Optional[str] = fields.TextField(description="Комментарий агента", null=True)
    admin_comment: Optional[str] = fields.TextField(description="Комментарий менеджера", null=True)

    agent_id: Optional[int]
    dispute_agent_id: Optional[int]

    class Meta:
        table = "users_checks"


class CheckRepo(BaseUserRepo, CRUDMixin):
    """
    Репозиторий проверки
    """
    model = Check
    q_builder: orm.QBuilder = orm.QBuilder(Check)
    c_builder: orm.ConverterBuilder = orm.ConverterBuilder(Check)
    a_builder: orm.AnnotationBuilder = orm.AnnotationBuilder(Check)
