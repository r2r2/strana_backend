from src.booking.services import CancelLoyaltyRewardService
from ..entities import BaseBookingCase


class CancelLoyaltyRewardCase(BaseBookingCase):
    """
    Отмена применения награды по программе лояльности.
    """

    def __init__(
        self,
        cancel_loyalty_reward_service: CancelLoyaltyRewardService,
    ) -> None:
        self.cancel_loyalty_reward_service: CancelLoyaltyRewardService = cancel_loyalty_reward_service

    async def __call__(
        self,
        booking_id: int,
        agent_amocrm_id: int | None = None,
    ) -> dict:

        result: dict = await self.cancel_loyalty_reward_service(
            booking_id=booking_id,
            agent_amocrm_id=agent_amocrm_id,
        )

        return result

