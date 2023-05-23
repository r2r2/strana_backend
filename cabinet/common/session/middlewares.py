import time
from http import HTTPStatus
from secrets import token_urlsafe
from typing import Any, Callable, Coroutine, Optional, Union

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware, DispatchFunction, RequestResponseEndpoint
from starlette.responses import JSONResponse
from starlette.types import ASGIApp

from .storages import SessionStorage
from ..redis import broker as redis, Redis


class SessionMiddleware(BaseHTTPMiddleware):
    """
    Adds .session attribute to fastapi.Request object
    """

    def __init__(
        self,
        key: str,
        len: int,
        domain: str,
        expire: int,
        cookie_len: int,
        amocrm_exclusion: str,
        broker: Optional[Any] = None,
        *args: Any,
        **kwargs: Any
    ) -> None:
        app: ASGIApp = kwargs.pop("app", None)
        dispatch: DispatchFunction = kwargs.pop("dispatch", None)
        super().__init__(app=app, dispatch=dispatch, *args)

        self.redis: Redis = redis
        if broker:
            self.redis: Redis = broker

        self.key: str = key
        self.len: int = len
        self.domain: str = domain
        self.expire: int = expire
        self.cookie_len: int = cookie_len
        self.amocrm_exclusion: list[str] = amocrm_exclusion

    async def dispatch(
        self, request: Request, call_next: Callable[[Request], Coroutine]
    ) -> Response:
        session_id: str = request.cookies.get(self.key)
        path_valid: bool = self.amocrm_exclusion not in request.scope["path"]
        if path_valid:
            request, session_id, generated_first = await self.process_request(
                request=request, session_id=session_id
            )
            response: Response = await call_next(request)
            response: Response = await self.process_response(
                response=response, session_id=session_id, generated_first=generated_first
            )
        else:
            response: Response = await call_next(request)
        return response

    async def process_request(
        self, request: Request, session_id: Optional[str]
    ) -> tuple[Request, str, bool]:
        generated_first: bool = False
        if not session_id:
            generated_first: bool = True
            session_id: str = token_urlsafe(self.len)
        else:
            if len(session_id) != self.cookie_len:
                await self.redis.delete(session_id)
                generated_first: bool = True
                session_id: str = token_urlsafe(self.len)
            else:
                session_data: Union[dict[str, Any], None] = await self.redis.get(session_id)
                if not session_data:
                    session_data: dict[str, Any] = dict()
                    await self.redis.set(key=session_id, value=session_data, expire=self.expire)
        request.scope["session"]: SessionStorage = await SessionStorage(session_id=session_id)
        return request, session_id, generated_first

    async def process_response(
        self, response: Response, session_id: Optional[str], generated_first: bool
    ) -> Response:
        if generated_first:
            response.set_cookie(
                key=self.key, value=session_id, domain=self.domain, samesite="none", secure=True
            )
        return response


class SessionTimeoutMiddleware(BaseHTTPMiddleware):
    """
    Middleware to invalidate session after specified timeout
    """
    def __init__(
        self,
        app: ASGIApp,
        key: str,
        last_activity_key: str,
        session_timeout: int = 20 * 60,
        broker: Optional[Any] = None,
        **_: Any,
    ):
        super().__init__(app=app)
        self.key: str = key
        self.last_activity_key: str = last_activity_key
        self.session_timeout: int = session_timeout

        self.redis: Redis = redis
        if broker:
            self.redis: Redis = broker

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        session_data: SessionStorage = request.session  # type: ignore
        last_activity_timestamp: int = await session_data.get(key=self.last_activity_key)
        current_timestamp: int = int(time.time())
        if not last_activity_timestamp:
            # Session was just created
            await session_data.set(key=self.last_activity_key, value=current_timestamp)
            response = await call_next(request)
            return response

        if current_timestamp - last_activity_timestamp > self.session_timeout:
            # Invalidate session
            session_id: str = request.cookies.get(self.key)
            await self.redis.delete(session_id)
            response = JSONResponse(
                status_code=HTTPStatus.UNAUTHORIZED,
                content={
                    "message": "Сессия истекла.",
                    "reason": "session_timeout",
                    "ok": False,
                },
            )
            for cookie in request.cookies:
                response.delete_cookie(key=cookie)
            return response
        else:
            # Update session timestamp and continue processing the request
            await session_data.set(key=self.last_activity_key, value=current_timestamp)
            response = await call_next(request)
            return response
