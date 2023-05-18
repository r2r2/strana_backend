from asyncio import sleep
from fastapi import WebSocket, WebSocketDisconnect
from typing import Optional, NoReturn, AsyncGenerator, Any

from ..entities import BaseNotificationManager
from ..use_cases import AgentsNotificationStreamCase


class AgentsNotificationsStreamManager(BaseNotificationManager):
    """
    Менеджер стриминга уведомлений агентов
    """

    def __init__(self, websocket: WebSocket, stream: AgentsNotificationStreamCase) -> None:
        self.websocket: WebSocket = websocket
        self.stream: AgentsNotificationStreamCase = stream

    async def __call__(self, agent_id: Optional[int] = None) -> NoReturn:
        if agent_id:
            await self.connect()
            try:
                while True:
                    streaming: AsyncGenerator[
                        AsyncGenerator[dict[str, Any], dict[str, Any]], None
                    ] = self.stream(agent_id=agent_id)
                    async for stream in streaming:
                        await self.websocket.send_text(await stream.__anext__())
                        data: dict[str, Any] = await self.websocket.receive_json()
                        try:
                            await stream.asend(data)
                        except StopAsyncIteration:
                            pass
                    await sleep(1)
            except WebSocketDisconnect:
                await self.disconnect()
        else:
            await self.disconnect()

    async def connect(self) -> None:
        await self.websocket.accept()

    async def disconnect(self) -> None:
        await self.websocket.close()
