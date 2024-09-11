from typing import Protocol

from src.core.types import UserId
from src.entities.matches import ChatType


class UnreadCountersOperationsProtocol(Protocol):
    async def get_unread_count(
        self,
        user_id: UserId,
        chat_type: ChatType | None = None,
    ) -> int: ...

    async def get_unread_count_by_chat(self, user_id: UserId, chat_id: int) -> int: ...

    async def get_unread_count_by_chats(self, user_id: UserId, chat_ids: list[int]) -> dict[int, int]: ...

    async def get_unread_count_by_match(self, user_id: UserId, match_id: int) -> int: ...

    async def get_unread_count_by_matches(self, user_id: UserId, match_ids: list[int]) -> dict[int, int]: ...
