from fastapi import Depends

from src.api.http.serializers.chats import ChatUnreadCountersResponse
from src.api.http.serializers.tickets import TicketUnreadCountersResponse
from src.core.common.caching import cached_method
from src.core.common.redis.cacher import RedisCacher
from src.core.common.redis.lib import IntegerSerializer
from src.core.di import Injected
from src.core.types import UserId
from src.entities.matches import ChatType
from src.entities.redis import UnreadCountCacheKey
from src.entities.tickets import TicketStatus
from src.entities.users import AuthPayload
from src.modules.storage.dependencies import inject_storage
from src.modules.storage.interface.storage import StorageProtocol
from src.modules.unread_counters.settings import UnreadCountersSettings


class UnreadCountersController:
    def __init__(
        self,
        settings: UnreadCountersSettings = Injected[UnreadCountersSettings],
        storage: StorageProtocol = Depends(inject_storage),
    ) -> None:
        self._storage = storage
        self._settings = settings
        self.cacher = RedisCacher(
            settings=settings.redis,
            alias="unread_counters",
            serializer=IntegerSerializer,
            default_ttl=settings.counters_ttl,
        )

    async def set_unread_count_by_chat_id(self, user_id: UserId, chat_id: int, value: int) -> None:
        await self.cacher.cache.set(
            key=UnreadCountCacheKey.BY_CHAT.format(user_id=user_id, chat_id=chat_id),
            value=value,
            ttl=self._settings.counters_ttl,
        )

    async def clean_unread_count_by_chat_id(self, user_id: UserId, chat_id: int) -> None:
        await self.cacher.cache.delete(
            UnreadCountCacheKey.BY_CHAT.format(user_id=user_id, chat_id=chat_id),
        )

    async def clean_unread_count_by_match_id(self, user_id: UserId, match_id: int) -> None:
        await self.cacher.cache.delete(
            UnreadCountCacheKey.BY_MATCH.format(user_id=user_id, match_id=match_id),
        )

    async def clean_total_unread_count(self, user_id: UserId) -> None:
        await self.cacher.cache.delete(
            UnreadCountCacheKey.TOTAL.format(user_id=user_id),
        )

    @cached_method(key_tpl=UnreadCountCacheKey.BY_CHAT)
    async def get_unread_count_by_chat_id(self, *, user_id: UserId, chat_id: int) -> int:
        return await self._storage.unread_counters.get_unread_count_by_chat(user_id, chat_id)

    @cached_method(
        keys_kwarg="chat_ids",
        single_key_tpl_name="chat_id",
        key_tpl=UnreadCountCacheKey.BY_CHAT,
    )
    async def get_unread_count_by_chat_ids(self, *, user_id: UserId, chat_ids: list[int]) -> dict[int, int]:
        if not chat_ids:
            return {}

        return await self._storage.unread_counters.get_unread_count_by_chats(user_id, chat_ids)

    @cached_method(key_tpl=UnreadCountCacheKey.BY_MATCH)
    async def get_unread_count_by_match_id(self, *, user_id: UserId, match_id: int) -> int:
        return await self._storage.unread_counters.get_unread_count_by_match(user_id, match_id)

    @cached_method(
        keys_kwarg="match_ids",
        single_key_tpl_name="match_id",
        key_tpl=UnreadCountCacheKey.BY_MATCH,
    )
    async def get_unread_count_by_match_ids(self, *, user_id: UserId, match_ids: list[int]) -> dict[int, int]:
        if not match_ids:
            return {}

        return await self._storage.unread_counters.get_unread_count_by_matches(user_id, match_ids)

    @cached_method(key_tpl=UnreadCountCacheKey.TOTAL)
    async def get_total_unread_count(self, *, user_id: UserId) -> int:
        return await self._storage.unread_counters.get_unread_count(user_id=user_id, chat_type=None)

    async def update_total_unread_count(self, *, user_id: UserId, update_by: int) -> None:
        await self.cacher.cache.increment(
            key=UnreadCountCacheKey.TOTAL.format(user_id=user_id),
            delta=update_by,
        )


class CountersController:
    def __init__(
        self,
        caching_controller: UnreadCountersController = Depends(),
        storage: StorageProtocol = Depends(inject_storage),
    ) -> None:
        self._caching_controller = caching_controller
        self._storage = storage

    async def get_unread_counters(self, user: AuthPayload) -> ChatUnreadCountersResponse:
        return ChatUnreadCountersResponse(
            total=await self._caching_controller.get_total_unread_count(user_id=user.id),
            by_chat_type={
                chat_type: await self._storage.unread_counters.get_unread_count(user.id, chat_type)
                for chat_type in ChatType
            },
        )

    async def get_ticket_counters(self, user: AuthPayload) -> TicketUnreadCountersResponse:
        return TicketUnreadCountersResponse(
            by_ticket_status={
                TicketStatus.NEW: await self._storage.tickets.count_tickets(TicketStatus.NEW),
                TicketStatus.IN_PROGRESS: await self._storage.tickets.count_tickets(TicketStatus.IN_PROGRESS, user.id),
            },
        )
