from datetime import datetime
from typing import Optional

from tortoise import Model, fields
from tortoise.fields import ForeignKeyNullableRelation

from common.orm.mixins import ReadWriteMixin, CountMixin
from src.users.repos import User
from src.agencies.repos import Agency

from ..entities import BaseNotificationRepo


class Notification(Model):
    """
    Уведомление
    """

    id: int = fields.BigIntField(description="ID", pk=True, index=True)
    message: Optional[str] = fields.TextField(description="Сообщение", null=True)
    is_read: bool = fields.BooleanField(description="Прочитано", default=False)
    is_sent: bool = fields.BooleanField(description="Отправлено", default=False)
    sent: Optional[datetime] = fields.DatetimeField(description="Время отправления", null=True)
    read: Optional[datetime] = fields.DatetimeField(description="Время просмотра", null=True)
    created: Optional[datetime] = fields.DatetimeField(description="Время создания", null=True)
    user: ForeignKeyNullableRelation[User] = fields.ForeignKeyField(
        description="Пользователь",
        model_name="models.User",
        on_delete=fields.CASCADE,
        related_name="notifications",
        null=True,
    )
    agency: ForeignKeyNullableRelation[Agency] = fields.ForeignKeyField(
        description="Агентство",
        model_name="models.Agency",
        on_delete=fields.CASCADE,
        related_name="notifications",
        null=True,
    )

    def __str__(self) -> str:
        return f"Уведомление #{self.id}"

    class Meta:
        table = "notifications_notification"


class NotificationRepo(BaseNotificationRepo, ReadWriteMixin, CountMixin):
    """
    Репозиторий уведомления
    """
    model = Notification
