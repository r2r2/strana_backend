import json
from typing import Any, Optional, Type

from aiofile import async_open
from jinja2 import Template
from src.notifications.repos import ClientNotificationRepo

from ..entities import BaseBookingService
from ..repos import Booking


class NotificationService(BaseBookingService):
    """Сервис создания оповещений."""

    _cache: dict[str, str] = {}

    def __init__(self, client_notification_repo: Type[ClientNotificationRepo]) -> None:
        self._client_notification_repo = client_notification_repo()

    async def __call__(
        self,
        *,
        booking: Booking,
        previous_online_purchase_step: str,
        template: str,
        params: Optional[dict[str, Any]] = None,
    ) -> None:
        if params is None:
            params = {}

        plain_notification_data = await self._provide_template_content(template)

        notification_json_body = await Template(
            plain_notification_data, enable_async=True
        ).render_async(**params)

        json_notification = json.loads(notification_json_body)

        await self._client_notification_repo.create(
            booking=booking,
            title=json_notification["title"],
            description=json_notification["description"],
            created_at_online_purchase_step=previous_online_purchase_step,
        )

    async def _provide_template_content(self, template: str) -> str:
        """provide_template_content"""
        if template not in self._cache:
            async with async_open(template) as file:
                plain_history_data = await file.read()
            self._cache[template] = plain_history_data
        return self._cache[template]
