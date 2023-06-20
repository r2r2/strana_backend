from datetime import datetime
from typing import Optional

from tortoise import Model, fields
from tortoise.fields import ForeignKeyRelation

from common import cfields, orm
from common.orm.mixins import CRUDMixin
from src.users.constants import UserPinningStatusType
from src.users.entities import BaseUserRepo


class UserPinningStatus(Model):
    """
    Статус закрепления пользователя
    """
    id: int = fields.IntField(description="ID", pk=True)
    updated_at: datetime = fields.DatetimeField(description="Когда обновлено", auto_now=True)
    status: Optional[str] = cfields.CharChoiceField(
        description="Статус",
        max_length=20,
        choice_class=UserPinningStatusType,
        default=UserPinningStatusType.UNKNOWN,
        null=False,
    )
    user: ForeignKeyRelation["User"] = fields.ForeignKeyField(
        description="Пользователь",
        model_name="models.User",
        on_delete=fields.CASCADE,
        related_name="users_pinning_status",
        null=False,
        index=True,
    )

    class Meta:
        table = "users_user_pinning_status"


class UserPinningStatusRepo(BaseUserRepo, CRUDMixin):
    """
    Репозиторий статуса закрепления пользователя
    """
    model = UserPinningStatus
    q_builder: orm.QBuilder = orm.QBuilder(UserPinningStatus)
    c_builder: orm.ConverterBuilder = orm.ConverterBuilder(UserPinningStatus)
    a_builder: orm.AnnotationBuilder = orm.AnnotationBuilder(UserPinningStatus)
