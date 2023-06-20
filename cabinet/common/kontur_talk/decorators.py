from typing import Callable, Coroutine

import structlog

from ..requests import CommonResponse

kontur_logger: structlog.getLogger = structlog.getLogger("Kontur Talk")


def kontur_logged(method: Callable[..., Coroutine]) -> Callable[..., Coroutine]:
    """
    Логирование запросов Kontur Talk
    """
    async def wrapper(self, *args, **kwargs) -> CommonResponse:
        response: CommonResponse = await method(self, *args, **kwargs)
        kontur_logger.debug("Kontur REQUEST", **response.__dict__)
        return response
    return wrapper
