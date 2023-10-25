from typing import Callable, Coroutine

import sentry_sdk
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response
import structlog

from common.handlers.exceptions import get_exc_info

logger = structlog.getLogger('errors')


class CatchExceptionsMiddleware(BaseHTTPMiddleware):
    """
    Logger Exceptions middleware
    """

    async def dispatch(
        self, request: Request, call_next: Callable[[Request], Coroutine]
    ) -> Response:
        try:
            return await call_next(request)
        except Exception as exception:
            sentry_sdk.capture_exception(exception)
            logger.error(f'UNCAUGHT_ERROR', exc_info=get_exc_info(exception))
            raise exception
