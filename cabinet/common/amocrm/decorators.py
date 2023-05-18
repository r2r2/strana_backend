# pylint: disable=protected-access
from typing import Callable, Coroutine

import structlog

from ..requests import CommonResponse

amo_logger = structlog.getLogger("AmoRequest")


def refresh_on_status(method: Callable[..., Coroutine]) -> Callable[..., Coroutine]:
    """
    Refreshes auth based on _refresh_statuses attribute of the class
    """

    async def decorated(self, *args, **kwargs) -> CommonResponse:
        response: CommonResponse = await method(self, *args, **kwargs)
        log_data: dict = dict(status=response.raw.status, method=response.raw.method, url=str(response.raw.url))
        amo_logger.debug("", request=args or kwargs, response=log_data)

        if response.status in self._refresh_statuses:
            await self._refresh_auth()
            response: CommonResponse = await method(self, *args, **kwargs)
        return response

    decorated.__name__ = method.__name__

    return decorated
