from typing import Any

from pyee.asyncio import AsyncIOEventEmitter

import structlog


class EventEmitter:
    ee: AsyncIOEventEmitter

    def __new__(cls, logger: Any | None = structlog.getLogger(__name__)):
        if not hasattr(cls, 'instance'):
            cls.instance = super(EventEmitter, cls).__new__(cls)
            logger.info("Starting Event Emitter")
            cls.ee = AsyncIOEventEmitter()
            # cls.ee.initialize_client()
        return cls.instance
