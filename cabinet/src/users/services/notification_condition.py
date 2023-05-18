from datetime import datetime
from typing import Any, Optional, Type
from uuid import uuid4

from pytz import UTC
from src.users.constants import UserType
from src.users.repos import RealIpUsersRepo, User, UserRepo
from src.users.repos.notification_mute import (NotificationMute,
                                               NotificationMuteRepo)


class NotificationConditionService:
    """
    Сервис для проверки необходимости отправки оповещений пользователю
    """

    limit = 3
    not_client_tag = "не клиент"

    def __init__(
        self,
        user_repo: Type[UserRepo],
        real_ip_repo: Type[RealIpUsersRepo],
        notification_mute_repo: Type[NotificationMuteRepo],
    ) -> None:
        self.user_repo = user_repo()
        self.real_ip_repo = real_ip_repo()
        self.notification_mute_repo = notification_mute_repo()

    def __call__(self, method):
        async def wrapper(init, phone: str, real_ip: str):
            real_ip_obj = await self.real_ip_repo.fetch_or_create(data=dict(real_ip=real_ip))
            await self.real_ip_repo.update(model=real_ip_obj, data=dict(times=real_ip_obj.times+1))

            filters: dict[str, Any] = dict(phone=phone, type=UserType.CLIENT)
            user: Optional[User] = await self.user_repo.retrieve(filters=filters)
            if user:
                user_tags = user.tags or []
                if user.amocrm_id and self.not_client_tag not in user_tags:
                    return await method(init, phone)

            data = dict(phone=phone, updated_at=datetime.now(tz=UTC))
            notification_mute: NotificationMute = await self.notification_mute_repo.fetch_or_create(data)
            if notification_mute.blocked:
                return dict(token=uuid4())

            if notification_mute.times == self.limit:
                notification_mute = await self.notification_mute_repo.update(notification_mute, dict(blocked=True))

            await self.notification_mute_repo.update(notification_mute, dict(times=notification_mute.times+1))
            return await method(init, phone)

        return wrapper
