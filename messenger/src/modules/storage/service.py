from contextlib import asynccontextmanager
from typing import AsyncGenerator, cast

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker

from src.core.common import ProtectedProperty
from src.modules.storage.helpers import (
    autocommit_session,
    create_engine,
    create_session,
)
from src.modules.storage.impl import (
    ChatOperations,
    CommonOperations,
    FileUploadsOperations,
    MatchOperations,
    MessageOperations,
    PushNotificationConfigsOperations,
    StatisticsOperations,
    TicketOperations,
    UnreadCountersOperations,
    UserOperations,
)
from src.modules.storage.interface import StorageProtocol, StorageServiceProto
from src.modules.storage.settings import DatabaseSettings


class Storage(StorageProtocol):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session
        self.chats = ChatOperations(session)
        self.messages = MessageOperations(session)
        self.matches = MatchOperations(session)
        self.common = CommonOperations(session)
        self.tickets = TicketOperations(session)
        self.users = UserOperations(session)
        self.file_uploads = FileUploadsOperations(session)
        self.unread_counters = UnreadCountersOperations(session)
        self.statistics = StatisticsOperations(session)
        self.push_notifications = PushNotificationConfigsOperations(session)

    async def commit_transaction(self) -> None:
        await self._session.commit()


class StorageService(StorageServiceProto):
    engine = ProtectedProperty[AsyncEngine]()
    sessionmaker = ProtectedProperty[async_sessionmaker[AsyncSession]]()

    def __init__(self, settings: DatabaseSettings) -> None:
        self._settings = settings

    async def health_check(self) -> bool:
        async with autocommit_session(self.sessionmaker) as session:
            result = await session.execute(text("SELECT 1"))
            return cast(bool, result.scalar_one() == 1)

    async def start(self) -> None:
        self.engine, self.sessionmaker = create_engine(self._settings)

    async def stop(self) -> None:
        await self.engine.dispose()

    @asynccontextmanager
    async def connect(self, autocommit: bool = False) -> AsyncGenerator[Storage, None]:
        context_method = autocommit_session if autocommit else create_session
        async with context_method(self.sessionmaker) as session:
            yield Storage(session)
