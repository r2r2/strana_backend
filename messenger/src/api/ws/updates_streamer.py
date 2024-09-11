from fastapi import APIRouter, Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from starlette.websockets import WebSocket

from src.modules.updates_streamer.controller import StreamerWebsocketHandler

updates_streamer_router = APIRouter(prefix="/updates/stream", tags=["Updates streamer"])


class WSBearer(HTTPBearer):
    async def __call__(self, request: WebSocket) -> HTTPAuthorizationCredentials | None:  # type: ignore
        return await super().__call__(request)  # type: ignore


security = WSBearer(auto_error=True, description="Authentication token")


@updates_streamer_router.websocket("")
async def connect_handler(
    request: WebSocket,
    auth: HTTPAuthorizationCredentials = Depends(security),
    controller: StreamerWebsocketHandler = Depends(),
) -> None:
    await controller.process_connection(request, auth.credentials)
