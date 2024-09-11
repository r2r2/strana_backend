from src.core.common.redis import create_redis_conn_pool
from src.core.types import LoggerType
from src.entities.users import Role
from src.modules.presence.constants import (
    ACTIVE_USERS_CACHE_KEY,
    CHAT_ACTIVITY_CACHE_KEY,
    CHAT_ACTIVITY_WILDCARD,
)
from src.modules.presence.interface import PackedUserData
from src.modules.presence.settings import RedisSettings


class PresenceStorage:
    def __init__(self, settings: RedisSettings, logger: LoggerType) -> None:
        self.logger = logger
        self.conn = create_redis_conn_pool(settings)

    async def health_check(self) -> bool:
        return await self.conn.ping()

    async def stop(self) -> None:
        await self.conn.close()

    async def get_active_users_in_chats(self, chat_ids: list[int], active_after: float) -> list[PackedUserData]:
        pipe = self.conn.pipeline(transaction=False)

        for chat_id in chat_ids:
            await pipe.zrangebyscore(
                name=CHAT_ACTIVITY_CACHE_KEY.format(chat_id=chat_id),
                min=active_after,
                max="inf",
            )

        result: list[list[bytes]] = await pipe.execute()
        return [PackedUserData.unpack(raw_user.decode()) for user_ids in result for raw_user in user_ids]

    async def get_active_users(self, active_after: float, filter_by_role: Role | None = None) -> list[PackedUserData]:
        results = await self.conn.zrangebyscore(
            name=ACTIVE_USERS_CACHE_KEY,
            min=active_after,
            max="inf",
        )
        result = [PackedUserData.unpack(raw_user.decode()) for raw_user in results]

        if filter_by_role:
            return [user for user in result if user.role == filter_by_role]

        return result

    async def set_last_user_activity(
        self,
        user_data: PackedUserData,
        active_at: float,
    ) -> None:
        await self.conn.zadd(
            name=ACTIVE_USERS_CACHE_KEY,
            mapping={user_data.pack(): active_at},
        )

    async def set_last_chat_activity(
        self,
        user_data: PackedUserData,
        chat_id: int,
        active_at: float,
    ) -> None:
        await self.conn.zadd(
            name=CHAT_ACTIVITY_CACHE_KEY.format(chat_id=chat_id),
            mapping={user_data.pack(): active_at},
        )

    async def cleanup_user_activity(self, active_before: float) -> None:
        await self.conn.zremrangebyscore(
            name=ACTIVE_USERS_CACHE_KEY,
            min=0,
            max=active_before,
        )

    async def cleanup_last_chat_activity(self, active_before: float) -> None:
        async for activity_chat_key in self.conn.scan_iter(match=CHAT_ACTIVITY_WILDCARD, _type="zset"):
            self.logger.debug(f"Scan: found {activity_chat_key}")
            await self.conn.zremrangebyscore(
                name=activity_chat_key,
                min=0,
                max=active_before,
            )
