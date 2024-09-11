from typing import AsyncContextManager, Protocol

from src.core.common import SupportsLifespan
from src.core.common.utility import SupportsHealthCheck

from .chats import ChatOperationsProtocol
from .common import CommonOperationsProtocol
from .file_uploads import FileUploadsOperationsProtocol
from .matches import MatchOperationsProtocol
from .messages import MessageOperationsProtocol
from .push_notifications import PushNotificationConfigsOperationsProtocol
from .statistics import StatsOperationsProtocol
from .tickets import TicketOperationsProtocol
from .unread_counters import UnreadCountersOperationsProtocol
from .users import UserOperationsProtocol


class StorageProtocol(Protocol):
    chats: ChatOperationsProtocol
    messages: MessageOperationsProtocol
    matches: MatchOperationsProtocol
    common: CommonOperationsProtocol
    tickets: TicketOperationsProtocol
    users: UserOperationsProtocol
    file_uploads: FileUploadsOperationsProtocol
    unread_counters: UnreadCountersOperationsProtocol
    statistics: StatsOperationsProtocol
    push_notifications: PushNotificationConfigsOperationsProtocol

    async def commit_transaction(self) -> None: ...


class StorageServiceProto(SupportsLifespan, SupportsHealthCheck, Protocol):
    def connect(self, autocommit: bool = False) -> AsyncContextManager[StorageProtocol]: ...
