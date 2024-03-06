from typing import Type
import structlog

from common.loyalty import LoyaltyAPI
from common.amocrm import AmoCRM
from src.booking.repos import BookingRepo, Booking
from src.booking.constants import CancelRewardComment
from src.booking.exceptions import BookingNotFoundError, BookingHasNoRewardError
from ..entities import BaseBookingService


class CancelLoyaltyRewardService(BaseBookingService):
    """
    Сервис отмены применения награды по программе лояльности.
    """

    def __init__(
        self,
        booking_repo: Type[BookingRepo],
        amocrm_class: Type[AmoCRM],
        loyalty_api: LoyaltyAPI,
    ) -> None:
        self.booking_repo: BookingRepo = booking_repo()
        self.amocrm_class: Type[AmoCRM] = amocrm_class
        self.loyalty_api: LoyaltyAPI = loyalty_api

        self.logger = structlog.getLogger(__name__)

    async def __call__(
        self,
        booking_id: int,
        agent_amocrm_id: int | None = None,
        comment: CancelRewardComment | None = None,
    ) -> dict:
        booking: Booking = await self._get_booking(
            booking_id=booking_id,
            agent_amocrm_id=agent_amocrm_id,
        )
        loyalty_discount = booking.loyalty_discount
        loyalty_discount_name = booking.loyalty_discount_name
        final_payment_amount_with_discount = booking.final_payment_amount

        updated_booking: Booking = await self.booking_repo.update(
            model=booking,
            data=dict(
                loyalty_discount_name=None,
                loyalty_discount=None,
                final_payment_amount=booking.final_payment_amount + booking.loyalty_discount,
            ),
        )
        self.logger.info(
            f"Для сделки {booking_id=} пересчитано значение стоимости сделки при отмене скидки "
            f"{loyalty_discount_name=} с {final_payment_amount_with_discount=} на "
            f"{updated_booking.final_payment_amount=}."
        )

        async with await self.amocrm_class() as amocrm:
            await amocrm.update_lead_v4(
                lead_id=updated_booking.amocrm_id,
                price_with_sales=updated_booking.final_payment_amount,
            )

            if not comment:
                message = (
                    f"Агент отменил скидку у сделки: {loyalty_discount_name}"
                    f"Сумма скидки: {loyalty_discount} руб."
                )
            else:
                message = (
                    f"Скидка {loyalty_discount_name} отменена, так как {comment.lower()}. "
                    f"Сумма скидки: {loyalty_discount} руб."
                )

            await amocrm.send_lead_note(
                lead_id=updated_booking.amocrm_id,
                message=message,
            )
            self.logger.info(
                f"Для сделки {booking_id=} в амо передано пересчитанное значение стоимости сделки при отмене скидки "
                f"{updated_booking.final_payment_amount=}."
            )

        if comment:
            async with self.loyalty_api as loyalty:
                await loyalty.cancel_booking_reward(booking_amocrm_id=booking.amocrm_id, comment=comment)

        return dict(ok=True)

    async def _get_booking(self, booking_id: int, agent_amocrm_id: int | None = None) -> Booking:
        filters: dict = dict(id=booking_id)
        if agent_amocrm_id:
            filters.update(agent__amocrm_id=agent_amocrm_id)

        booking: Booking = await self.booking_repo.retrieve(filters=filters)
        if not booking:
            raise BookingNotFoundError

        if not booking.loyalty_discount or not booking.loyalty_discount_name:
            raise BookingHasNoRewardError

        return booking

