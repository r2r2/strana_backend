from typing import Any, Type, Union

from src.booking.loggers.wrappers import booking_changes_logger

from ..constants import (BookingCreatedSources, BookingStages,
                         BookingSubstages, PaymentStatuses)
from ..entities import BaseBookingCase
from ..event_emitter_handlers import event_emitter
from ..exceptions import BookingNotFoundError, BookingTimeOutError
from ..mixins import BookingLogMixin
from ..models import RequestFastAcceptContractModel
from ..repos import Booking, BookingRepo


class FastAcceptContractCase(BaseBookingCase, BookingLogMixin):
    """
    Принятие оферты для быстрой брони
    """

    def __init__(
        self,
        booking_repo: Type[BookingRepo],
    ) -> None:
        self.booking_repo: BookingRepo = booking_repo()
        self.booking_update = booking_changes_logger(
            self.booking_repo.update, self, content="Принятие оферты для быстрой брони",
        )

    async def __call__(
        self, user_id: int, origin: Union[str, None], payload: RequestFastAcceptContractModel
    ) -> Booking:
        booking: Booking = await self.booking_repo.retrieve(
            filters=dict(id=payload.booking_id),
            related_fields=["project__city", "user"],
        )
        if not booking:
            raise BookingNotFoundError

        if not booking.time_valid():
            raise BookingTimeOutError

        old_group_status = booking.amocrm_substage if booking.amocrm_substage else None
        if booking.amocrm_substage in (
            BookingSubstages.MORTGAGE_DONE,
            BookingSubstages.MORTGAGE_LEAD,
            BookingSubstages.MORTGAGE_FILED,
            BookingSubstages.APPLY_FOR_A_MORTGAGE,
        ):
            # Не меняем статус, если это ипотека
            amocrm_substage = booking.amocrm_substage
        else:
            amocrm_substage = BookingSubstages.BOOKING

        data: dict[str, Any] = dict(
            amocrm_stage=BookingStages.BOOKING,
            payment_status=PaymentStatuses.CREATED,
            amocrm_substage=amocrm_substage,
            profitbase_booked=True,
            contract_accepted=payload.contract_accepted,
        )
        booking: Booking = await self.booking_update(booking=booking, data=data)
        # event_emitter.ee.emit(
        #     event='accept_contract',
        #     booking=booking,
        #     user=booking.user,
        #     old_group_status=old_group_status,
        #     city=booking.project.city.slug if booking.project.city else None,
        # )
        return booking
