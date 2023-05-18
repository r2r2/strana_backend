from tortoise import Model, fields
from tortoise.fields import ForeignKeyNullableRelation

from common.orm.mixins import CreateMixin, ListMixin
from common.loggers.repos import AbstractLogMixin
from ..repos import User
from ..entities import BaseUserRepo


class UserLog(Model, AbstractLogMixin):
    """
    Лог пользователя
    """

    user: ForeignKeyNullableRelation[User] = fields.ForeignKeyField(
        description="Пользователь",
        model_name="models.User",
        related_name="user_logs",
        null=True
    )

    class Meta:
        table = "users_userlog"


class UserLogRepo(BaseUserRepo, CreateMixin, ListMixin):
    """
    Репозиторий лога пользователя
    """

    model = UserLog
