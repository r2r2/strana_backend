# pylint: disable=protected-access
import traceback
from functools import wraps
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


def handle_amocrm_webhook_errors(func: Callable[..., Coroutine]) -> Callable[..., Coroutine]:
    """
    Decorator for AmoCRM webhook errors handling
    """
    @wraps(func)
    async def wrapper(*args, **kwargs):
        logger = structlog.get_logger(func.__name__)
        try:
            return await func(*args, **kwargs)
        except Exception as e:
            exception_message = str(e)
            traceback_str = traceback.format_exc()
            logger.error(f"AmoCRM webhook error: {exception_message}\nTraceback:\n{traceback_str}")
    return wrapper
