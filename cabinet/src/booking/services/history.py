from typing import Type, Optional, Any

from aiofile import async_open
from jinja2 import Template

from ..entities import BaseBookingService
from ..repos import BookingHistoryRepo, Booking
from ..repos.booking_history import BookingHistoryDocument


class HistoryService(BaseBookingService):
    """Сервис создания записей в истории сделок клиента."""

    _cache: dict[str, str] = {}

    def __init__(self, booking_history_repo: Type[BookingHistoryRepo]) -> None:
        self._booking_history_repo = booking_history_repo()

    async def execute(
        self,
        booking: Booking,
        previous_online_purchase_step: str,
        template: str,
        params: Optional[dict[str, Any]] = None,
        documents: Optional[list[list[BookingHistoryDocument]]] = None,
    ) -> None:
        """Создание записи в истории сделок клиента."""
        message = await self.render_message(template, params if params is not None else {})
        await self._booking_history_repo.create(
            booking=booking,
            previous_online_purchase_step=previous_online_purchase_step,
            documents=documents,
            message=message,
        )

    async def render_message(self, template: str, params: dict[str, Any]) -> str:
        plain_history_data = await self._provide_template_content(template)
        plain_history_data = plain_history_data.replace("\n", "")
        return await Template(
            plain_history_data, enable_async=True, trim_blocks=True, lstrip_blocks=True
        ).render_async(**params)

    async def _provide_template_content(self, template: str) -> str:
        if template not in self._cache:
            async with async_open(template) as file:
                plain_history_data = await file.read()
            self._cache[template] = plain_history_data
        return self._cache[template]
