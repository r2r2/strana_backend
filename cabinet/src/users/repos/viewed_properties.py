from tortoise import Model, fields

from common.models import TimeBasedMixin
from common.orm.mixins import ReadWriteMixin
from src.users.entities import BaseUserRepo


class UserViewedProperty(Model, TimeBasedMixin):
    """
    Модель просмотренных квартир
    """
    id = fields.IntField(pk=True)
    client = fields.ForeignKeyField(
        "models.User",
        related_name="viewing_client",
        on_delete=fields.CASCADE,
        description="Пользователь просмотревший квартиру"
    )
    property = fields.ForeignKeyField(
        "models.Property",
        related_name="user_favorite_property",
        on_delete=fields.CASCADE,
        description="Просмотренная квартира"
    )

    class Meta:
        table = "users_viewed_property"


class UserViewedPropertyRepo(BaseUserRepo, ReadWriteMixin):
    """
    Репозиторий просмотренных квартир
    """
    model: UserViewedProperty = UserViewedProperty
