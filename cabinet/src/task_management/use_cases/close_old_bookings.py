from datetime import datetime, timedelta
from typing import Any, Type

import structlog

from common.amocrm import AmoCRM
from pytz import UTC

from src.booking.constants import BookingSubstages
from src.booking.repos import Booking, BookingRepo
from src.task_management.constants import BOOKING_UPDATE_FIXATION_STATUSES


class CloseOldBookingCase:
    FIXATION_TASK_CHAIN_NAME = "Продление сделки"

    def __init__(
        self,
        booking_repo: type[BookingRepo],
        amocrm_class: type[AmoCRM],
    ):
        self.booking_repo: BookingRepo = booking_repo()
        self.amocrm_class: type[AmoCRM] = amocrm_class
        self.logger = structlog.get_logger()

    async def __call__(self, days: int, debug: bool) -> list[Booking]:
        self.logger.info("Запущен скрипт для закрытия старых сделок")
        needed_close_bookings = await self._get_bookings(days)
        self.logger.info(f"Старых сделок для закрытия - {len(needed_close_bookings)}")

        if not debug:
            await self._update_amocrm_leads(needed_close_bookings)
            await self._update_booking_data(needed_close_bookings)

        return needed_close_bookings

    async def _update_booking_data(self, bookings: list[Booking]) -> None:
        """
        Отвязывание всех сделок от агентов.
        Ставим статус ЗАКРЫТО и НЕ РЕАЛИЗОВАНО, active=False.
        """
        filters = dict(id__in=[booking.id for booking in bookings])
        update_data: dict[str, Any] = dict(
            agent_id=None,
            agency_id=None,
            amocrm_stage=Booking.stages.DDU_UNREGISTERED,
            amocrm_substage=Booking.substages.UNREALIZED,
            active=False
        )
        await self.booking_repo.bulk_update(filters=filters, data=update_data)

    async def _update_amocrm_leads(self, bookings: list[Booking]):
        """
        Обновить сделки в амо.
        Всем сделкам ставим статус "закрыто и не реализовано"
        """
        async with await self.amocrm_class() as amocrm:
            for booking in bookings:
                if booking.amocrm_id:
                    lead_options: dict[str, Any] = dict(
                        status=BookingSubstages.UNREALIZED,
                        lead_id=booking.amocrm_id,
                        city_slug=booking.project.city.slug,
                    )
                    await amocrm.update_lead(**lead_options)

    async def _get_bookings(self, days) -> list[Booking]:
        """
        Получение списка сделок требующих закрытия.
        """
        needed_close_bookings: list[Booking] = await self.booking_repo.list(
            filters=dict(
                created__lte=datetime.now(tz=UTC) - timedelta(days=days),
                amocrm_status__group_status__name__in=BOOKING_UPDATE_FIXATION_STATUSES,
            ),
            prefetch_fields=['project__city',],
        )

        return needed_close_bookings
