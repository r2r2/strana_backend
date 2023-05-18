from typing import Any
from fastapi import WebSocket, Depends

from common import dependencies
from src.users import constants as users_constants
from src.notifications import use_cases, managers
from src.notifications import repos as notifications_repos


async def agents_notifications_ws(
    websocket: WebSocket,
    agent_id: int = Depends(dependencies.WSCurrentUserId(user_type=users_constants.UserType.AGENT)),
):
    """
    Отправка уведомлений агенту
    """
    resources: dict[str, Any] = dict(notification_repo=notifications_repos.NotificationRepo)
    agents_notifications_stream: use_cases.AgentsNotificationStreamCase = use_cases.AgentsNotificationStreamCase(
        **resources
    )
    resources: dict[str, Any] = dict(websocket=websocket, stream=agents_notifications_stream)
    agents_notifications_manager: managers.AgentsNotificationsStreamManager = managers.AgentsNotificationsStreamManager(
        **resources
    )
    await agents_notifications_manager(agent_id=agent_id)
