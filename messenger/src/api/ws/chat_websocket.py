from fastapi import APIRouter, Depends, Query
from starlette.websockets import WebSocket

from src.modules.chat.service import ChatService

chat_ws_api_router = APIRouter(prefix="/ws/chat", tags=["Chat"])


@chat_ws_api_router.websocket("", name="Connect to socket")
async def connect_handler(
    request: WebSocket,
    token: str = Query(..., description="Authentication token"),
    controller: ChatService = Depends(),
) -> None:
    await controller.process_connection(request, token)
