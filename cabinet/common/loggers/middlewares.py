import uuid
from typing import Callable, Coroutine

import structlog
from config import amocrm_config
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

logger = structlog.get_logger("response")
amo_logger = structlog.get_logger("AmoWebhook")


class LoggerMiddleware(BaseHTTPMiddleware):
    """
    Logger middleware
    """

    async def dispatch(
        self, request: Request, call_next: Callable[[Request], Coroutine]
    ) -> Response:
        structlog.contextvars.clear_contextvars()
        structlog.contextvars.bind_contextvars(
            request_id=str(uuid.uuid4()),
            method=request.method,
            view=request.url.path
        )
        response: Response = await call_next(request)
        logger.info(status_code=response.status_code)
        return response


class AMOWebhookLoggerMiddleware(BaseHTTPMiddleware):
    """
    AMOWebhook Logger Middleware
    """

    async def dispatch(
        self, request: Request, call_next: Callable[[Request], Coroutine]
    ) -> Response:
        if request.url.path.endswith(amocrm_config.get('secret')):
            response = await call_next(request)
            amo_logger.debug("", request=request.__dict__, response=response.__dict__)
            return response
        return await call_next(request)
