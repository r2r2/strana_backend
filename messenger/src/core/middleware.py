import time
from uuid import uuid4

from starlette.requests import HTTPConnection
from starlette.types import ASGIApp, Receive, Scope, Send

from src.core.logger import LoggerName, add_to_log_ctx, get_logger

MISSING = "<>"


class RequestLoggingMiddleware:
    @staticmethod
    def _generate_request_id() -> str:
        return str(uuid4())

    def __init__(self, app: ASGIApp):
        self.app = app
        self.logger = get_logger(LoggerName.ACCESS)

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        match scope["type"]:
            case "lifespan":
                await self.app(scope, receive, send)
                return
            case "websocket":
                method = "ws"
            case "http":
                method = scope["method"]
            case _:
                method = "unknown"

        conn = HTTPConnection(scope)

        start_time = time.perf_counter()

        add_to_log_ctx(cid=self._generate_request_id())

        log_kwargs = {
            "ip": conn.client.host if conn.client else MISSING,
            "method": method,
            "user_agent": conn.headers.get("User-Agent", MISSING),
            "full_url": str(conn.url),
            "path": conn.url.path,
        }

        if method == "ws":
            self.logger.info(f"Websocket request received: {conn.url.path}", **log_kwargs)

        await self.app(scope, receive, send)

        end_time = time.perf_counter()

        self.logger.info(
            f"{method.upper()} request: {conn.url.path}",
            duration=round(end_time - start_time, 3),
            **log_kwargs,
        )
