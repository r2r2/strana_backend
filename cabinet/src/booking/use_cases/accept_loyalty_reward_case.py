from typing import Type
import structlog

from common.amocrm import AmoCRM
from src.booking.repos import BookingRepo, Booking
from src.booking.exceptions import BookingNotFoundError, BookingAlreadyHasRewardError
from src.users.repos import UserRepo
from ..models import RequestLoyaltyRewardModel
from ..entities import BaseBookingCase


class AcceptLoyaltyRewardCase(BaseBookingCase):
    """
    Применение награды по программе лояльности.
    """

    def __init__(
        self,
        booking_repo: Type[BookingRepo],
        amocrm_class: Type[AmoCRM],
    ) -> None:
        self.booking_repo: BookingRepo = booking_repo()
        self.amocrm_class: Type[AmoCRM] = amocrm_class

        self.logger = structlog.getLogger(__name__)

    async def __call__(
        self,
        booking_id: int,
        agent_amocrm_id: int,
        payload: RequestLoyaltyRewardModel,
    ) -> dict:
        booking: Booking = await self._get_booking(
            booking_id=booking_id,
            agent_amocrm_id=agent_amocrm_id,
        )

        loyalty_discount = booking.final_payment_amount * payload.loyalty_discount_percent / 100

        updated_booking: Booking = await self.booking_repo.update(
            model=booking,
            data=dict(
                loyalty_discount_name=payload.loyalty_discount_name,
                loyalty_discount=loyalty_discount,
                final_payment_amount=booking.final_payment_amount - loyalty_discount,
            ),
        )
        self.logger.info(
            f"Для сделки {booking_id=} пересчитано значение стоимости сделки с учетом скидки "
            f"{loyalty_discount=} с {booking.final_payment_amount=} на {updated_booking.final_payment_amount=}."
        )

        async with await self.amocrm_class() as amocrm:
            await amocrm.update_lead_v4(
                lead_id=updated_booking.amocrm_id,
                price_with_sales=updated_booking.final_payment_amount,
            )
            await amocrm.send_lead_note(
                lead_id=updated_booking.amocrm_id,
                message=f"Агент применил скидку к сделке: {updated_booking.loyalty_discount_name}",
            )
            self.logger.info(
                f"Для сделки {booking_id=} в амо передано пересчитанное значение стоимости сделки с учетом скидки "
                f"{updated_booking.final_payment_amount=}."
            )

        return dict(ok=True)

    async def _get_booking(self, booking_id: int, agent_amocrm_id: int) -> Booking:
        booking: Booking = await self.booking_repo.retrieve(
            filters=dict(
                id=booking_id,
                agent__amocrm_id=agent_amocrm_id,
            ),
        )
        if not booking:
            raise BookingNotFoundError

        if booking.loyalty_discount or booking.loyalty_discount_name:
            raise BookingAlreadyHasRewardError

        return booking

