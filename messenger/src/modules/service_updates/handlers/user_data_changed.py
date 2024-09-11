from typing import Any

from src.core.types import ConnectionId
from src.entities.redis import RedisPubSubChannelName
from src.entities.users import Role
from src.modules.service_updates.entities import UserDataChanged
from src.modules.service_updates.handlers.base import BaseUpdateHandler
from src.modules.users_cache.service import UserCacheKey


class UserDataChangedUpdateHandler(BaseUpdateHandler[UserDataChanged], update_type=UserDataChanged):
    async def handle(self, cid: ConnectionId | None, update: UserDataChanged) -> None:
        async with self.storage_srvc.connect(autocommit=True) as db:
            user = await db.users.get_by_id(user_id=update.user_id)

            if not user and update.role == Role.SCOUT:
                await self.auth_srvc.grant(user_id=update.user_id, role=Role.SCOUT.value)

            kwargs: dict[str, Any] = {
                "user_id": update.user_id,
                "name": update.name,
                "scout_number": update.scout_number,
            }
            if not user:
                kwargs["role"] = update.role

            method = db.users.create if not user else db.users.update

            await method(**kwargs)
            await self.redis_publisher.redis_conn.delete(UserCacheKey.DATA.format(user_id=update.user_id))
            await self.redis_publisher.publish(
                channel_name=RedisPubSubChannelName.USER_DATA_CACHE_INVALIDATION.value,
                data=f"{self._id}:{update.user_id}".encode(),
            )
