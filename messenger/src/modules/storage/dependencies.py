from typing import AsyncGenerator

from src.core.di import Injected
from src.modules.storage.interface import StorageProtocol, StorageServiceProto


async def inject_storage(
    storage_service: StorageServiceProto = Injected[StorageServiceProto],
) -> AsyncGenerator[StorageProtocol, None]:
    async with storage_service.connect(autocommit=False) as storage:
        yield storage
        await storage.commit_transaction()
