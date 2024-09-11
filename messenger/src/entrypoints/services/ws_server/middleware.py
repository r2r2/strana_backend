from fastapi import WebSocket, status
from starlette.types import ASGIApp, Receive, Scope, Send

from src.core.logger import LoggerName, get_logger
from src.entrypoints.services.ws_server.settings import WSServiceSettings
from src.modules.connections import ConnectionsServiceProto

MISSING = "<>"


class WSConnectionsLimitMiddleware:
    def __init__(self, app: ASGIApp):
        self.app = app
        self.logger = get_logger(LoggerName.WS)

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "websocket":
            await self.app(scope, receive, send)
            return

        ws = WebSocket(scope, receive, send)
        connections_service: ConnectionsServiceProto = ws.app.state.connections
        app_settings: WSServiceSettings = ws.app.state.settings
        client_ip = ws.client.host if ws.client else None

        if connections_service.get_connections_count_by_ip(client_ip) >= app_settings.max_connections_per_ip:
            self.logger.warning("Connections limit reached", ip=client_ip)
            await ws.close(
                code=status.WS_1013_TRY_AGAIN_LATER,
                reason="Connection limit exceeded",
            )
            return

        await self.app(scope, receive, send)
