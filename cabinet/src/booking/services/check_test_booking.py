from copy import copy
from datetime import datetime
from typing import Any, Optional, Type, Union

import structlog

from common.amocrm.types import AmoLead
from common.bitrix import Bitrix
from src.booking.constants import TestBookingStatuses

from ..entities import BaseBookingService
from ..repos import TestBookingRepo, TestBooking
from ..types import (
    BookingAmoCRM,
    BookingORM,
)


class CheckTestBookingService(BaseBookingService):
    """
    Проверка Тестовых бронирований
    """
    mail_event_slug = "check_test_booking_notification"

    def __init__(
        self,
        test_booking_repo: Type[TestBookingRepo],
        amocrm_class: Type[BookingAmoCRM],
        bitrix_class: Type[Bitrix],
        orm_class: Optional[BookingORM] = None,
        orm_config: Optional[dict[str, Any]] = None,
        logger: Optional[Any] = structlog.getLogger(__name__),
    ) -> None:
        self.logger = logger
        self.test_booking_repo: TestBookingRepo = test_booking_repo()
        self.amocrm_class: Type[BookingAmoCRM] = amocrm_class
        self.bitrix_class: Type[Bitrix] = bitrix_class
        self.orm_class: Union[Type[BookingORM], None] = orm_class
        self.orm_config: Union[dict[str, Any], None] = copy(orm_config)
        if self.orm_config:
            self.orm_config.pop("generate_schemas", None)

    async def __call__(self) -> None:
        """
        Один раз в день в 21.00 по МСК запускаем задачу, которая чекает, удалены ли сделки в АМО
        (помним, что амо перегружать запросами нельзя).
         Только для сделок, которые имеют статус "Есть в АМО" и у которых нет флага "Исключить из проверки".
         Фиксирует время чека для них.
         Если есть хотя бы 1 неудаленная сделка пишет сообщение в чат в леночке следующего формата
        """
        test_bookings = await self._get_test_bookings()
        leads = await self._receive_leads_from_amo(test_bookings)
        await self._update_test_bookings(test_bookings, leads)
        not_deleted_test_bookings = await self._get_test_bookings()
        if not_deleted_test_bookings is not None:
            message = self._make_message(not_deleted_test_bookings)
            await self._send_message(message)

    async def _get_test_bookings(self) -> list[TestBooking] | None:
        filters: dict[str, Any] = dict(status=TestBookingStatuses.IN_AMO, is_check_skipped=False)
        test_bookings: list[TestBooking] = await self.test_booking_repo.list(filters=filters)

        return test_bookings

    async def _receive_leads_from_amo(self, test_bookings: list[TestBooking] | None) -> list[AmoLead] | None:
        if not test_bookings:
            return

        lead_ids = [test_booking.amocrm_id for test_booking in test_bookings]

        if lead_ids:
            async with await self.amocrm_class() as amocrm:
                leads: list[AmoLead] = await amocrm.fetch_leads(lead_ids=lead_ids)
                return leads

    async def _update_test_bookings(self, test_bookings: list[TestBooking] | None, leads: list[AmoLead] | None) -> None:
        for test_booking in test_bookings:
            data = dict(last_check_at=datetime.now())
            if test_booking.amocrm_id not in [str(lead.id) for lead in leads]:
                data.update(status=TestBookingStatuses.NOT_IN_AMO)
            await self.test_booking_repo.update(test_booking, data=data)

    @staticmethod
    def _make_message(not_deleted_test_bookings: list[TestBooking] | None) -> str | None:
        if not not_deleted_test_bookings:
            return

        dev_not_deleted_test_bookings = len([test_booking for test_booking in not_deleted_test_bookings if
                                             test_booking.info == "dev"])
        stage_not_deleted_test_bookings = len([test_booking for test_booking in not_deleted_test_bookings if
                                               test_booking.info == "stage"])
        prod_not_deleted_test_bookings = len([test_booking for test_booking in not_deleted_test_bookings if
                                              test_booking.info == "prod"])

        message = f"Внимание! {len(not_deleted_test_bookings)} сделок в АМО не были удалены в конце дня.\n" \
                  f"Окружение dev: {dev_not_deleted_test_bookings} сделок.\n" \
                  f"Окружение stage: {stage_not_deleted_test_bookings} сделок.\n" \
                  f"Окружение prod: {prod_not_deleted_test_bookings} сделок."

        return message

    async def _send_message(self, message):
        self.logger.debug(f"Send message: {message}")
        async with await self.bitrix_class() as bitrix:
            data: dict[str, bool] = await bitrix.send_message_in_chat(message=message)
            self.logger.debug(f"{data=}")
            return data
