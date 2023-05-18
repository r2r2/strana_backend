from typing import Coroutine


def get_websockets() -> dict[Coroutine, str]:
    from src.notifications import ws as notifications_ws

    websockets: dict[Coroutine, str] = dict()

    websockets[notifications_ws.agents_notifications_ws] = "notifications/agents"

    websockets: dict[Coroutine, str] = dict(
        map(lambda x: (x[0], f"/ws/{x[1]}"), websockets.items())
    )

    return websockets
