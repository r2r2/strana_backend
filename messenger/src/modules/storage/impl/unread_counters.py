from sqlalchemy.ext.asyncio import AsyncSession

from src.core.types import UserId
from src.entities.matches import ChatType
from src.modules.storage.impl.query_builders.unread_counters import UnreadCountersQueryBuilder
from src.modules.storage.interface.unread_counters import UnreadCountersOperationsProtocol


class UnreadCountersOperations(UnreadCountersOperationsProtocol):
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_unread_count(
        self,
        user_id: UserId,
        chat_type: ChatType | None = None,
    ) -> int:
        query_builder = UnreadCountersQueryBuilder(user_id=user_id)
        query = query_builder.build_total_unread_count_query(chat_type=chat_type)
        result = await self.session.execute(query)
        return result.scalar_one_or_none() or 0

    async def get_unread_count_by_chat(self, user_id: UserId, chat_id: int) -> int:
        query_builder = UnreadCountersQueryBuilder(user_id=user_id)
        query = query_builder.build_unread_count_by_chat_query(chat_id=chat_id)
        result = await self.session.execute(query)
        return result.scalar_one_or_none() or 0

    async def get_unread_count_by_chats(self, user_id: UserId, chat_ids: list[int]) -> dict[int, int]:
        query_builder = UnreadCountersQueryBuilder(user_id=user_id)
        query = query_builder.build_unread_count_by_chats_query(chat_ids=chat_ids)
        query_result = await self.session.execute(query)

        result = {chat_id: 0 for chat_id in chat_ids}
        for unread_count, chat_id in query_result.tuples():
            result[chat_id] = unread_count

        return result

    async def get_unread_count_by_match(self, user_id: UserId, match_id: int) -> int:
        query_builder = UnreadCountersQueryBuilder(user_id=user_id)
        query = query_builder.build_unread_count_by_match_query(match_id=match_id)
        result = await self.session.execute(query)
        return result.scalars().first() or 0

    async def get_unread_count_by_matches(self, user_id: UserId, match_ids: list[int]) -> dict[int, int]:
        query_builder = UnreadCountersQueryBuilder(user_id=user_id)
        query = query_builder.build_unread_count_by_matches_query(match_ids=match_ids)
        query_result = await self.session.execute(query)

        result = {match_id: 0 for match_id in match_ids}
        for unread_count, match_id in query_result.tuples():
            result[match_id] = unread_count

        return result
