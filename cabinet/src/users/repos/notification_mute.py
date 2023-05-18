from datetime import datetime
from typing import Any

from common.orm.mixins import (CreateMixin, DeleteMixin, ExistsMixin,
                               RetrieveMixin, UpdateMixin)
from tortoise import Model, fields

from ..entities import BaseUserRepo


class NotificationMute(Model):
    """
    Запреты на отправку оповещений пользователям
    """

    phone: str = fields.CharField(description="Номер телефона", max_length=20, index=True, null=True)
    blocked: bool = fields.BooleanField(description="Заблокирован", default=False)
    times: int = fields.IntField(description="Количество запросов", default=0)
    created_at: datetime = fields.DatetimeField(description="Время создания", auto_now_add=True)
    updated_at: datetime = fields.DatetimeField(description="Время обновления", auto_now=True)

    def __str__(self) -> str:
        return str(self.phone)

    class Meta:
        table = "users_notification_mute"


class NotificationMuteRepo(BaseUserRepo, CreateMixin, ExistsMixin, RetrieveMixin, UpdateMixin, DeleteMixin):
    """
    Репозиторий запретов на отправку оповещений пользователей
    """
    model = NotificationMute

    async def fetch_or_create(self, data: dict[str, Any]) -> NotificationMute:
        """
        Создание запрета, если не существует
        """
        notification_mute = await self.retrieve(filters=dict(phone=data["phone"]))

        if not notification_mute:
            notification_mute = await super().create(data)
        return notification_mute


class RealIpUsers(Model):
    """
    IP адреса клиентов
    """

    real_ip: str = fields.CharField(description="IP адрес клиента", max_length=20)
    blocked: bool = fields.BooleanField(description="Заблокирован", default=False)
    times: int = fields.IntField(description="Количество запросов", default=0)
    created_at: datetime = fields.DatetimeField(description="Время создания", auto_now_add=True)
    updated_at: datetime = fields.DatetimeField(description="Время обновления", auto_now=True)

    def __str__(self) -> str:
        return str(self.real_ip)

    class Meta:
        table = "users_real_ip"


class RealIpUsersRepo(BaseUserRepo, CreateMixin, ExistsMixin, RetrieveMixin, UpdateMixin, DeleteMixin):
    """
    Репозиторий запретов на отправку оповещений пользователей
    """
    model = RealIpUsers

    async def fetch_or_create(self, data: dict[str, Any]) -> RealIpUsers:
        """
        Создание запрета, если не существует
        """
        notification_mute = await self.retrieve(filters=dict(real_ip=data["real_ip"]))

        if not notification_mute:
            notification_mute = await super().create(data)
        return notification_mute
