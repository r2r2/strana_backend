from typing import Type
import structlog

from src.booking.repos import BookingRepo, Booking
from src.booking.exceptions import BookingNotFoundError
from src.users.constants import UserType
from ..repos import AgentRepo, User
from ..models import LoyaltyStatusRequestModel
from ..exceptions import AgentNotFoundError
from ..entities import BaseAgentCase


class GetCurrentAccountLoyaltyPointsCase(BaseAgentCase):
    """
    Импорт данных агента по программе лояльности из МС Лояльности.
    """

    def __init__(
        self,
        agent_repo: Type[AgentRepo],
        booking_repo: Type[BookingRepo],
        logger=structlog.getLogger(__name__),
    ) -> None:
        self.agent_repo: AgentRepo = agent_repo()
        self.booking_repo: BookingRepo = booking_repo()
        self.logger = logger

    async def __call__(self, agent_amocrm_id: int, payload: LoyaltyStatusRequestModel) -> None:
        agent: User = await self.agent_repo.retrieve(
            filters=dict(
                amocrm_id=agent_amocrm_id,
                type__in=[UserType.AGENT, UserType.REPRES],
            )
        )
        if not agent:
            raise AgentNotFoundError

        loyalty_status_data = dict(
            loyalty_point_amount=payload.loyalty_point_amount,
            date_assignment_loyalty_status=payload.date_assignment_loyalty_status,
            is_offer_accepted=payload.is_offer_accepted,
            loyalty_status_name=payload.loyalty_status.loyalty_status_name,
        )
        if loyalty_status_icon_data := payload.loyalty_status.loyalty_status_icon:
            loyalty_status_data.update(loyalty_status_icon=loyalty_status_icon_data.get("src"))
        if loyalty_status_level_icon_data := payload.loyalty_status.loyalty_status_level_icon:
            loyalty_status_data.update(loyalty_status_level_icon=loyalty_status_level_icon_data.get("src"))
        if loyalty_status_substrate_card_data := payload.loyalty_status.loyalty_status_substrate_card:
            loyalty_status_data.update(loyalty_status_substrate_card=loyalty_status_substrate_card_data.get("src"))
        if loyalty_status_icon_profile_data := payload.loyalty_status.loyalty_status_icon_profile:
            loyalty_status_data.update(loyalty_status_icon_profile=loyalty_status_icon_profile_data.get("src"))

        await self.agent_repo.update(model=agent, data=loyalty_status_data)
        self.logger.info(f"Loyalty payload booking - {payload.booking}")

        if payload.booking and payload.booking.amocrm_id and payload.booking.point_amount:
            booking: Booking = await self.booking_repo.retrieve(filters=dict(amocrm_id=payload.booking.amocrm_id))
            if not booking:
                raise BookingNotFoundError

            updated_booking = await self.booking_repo.update(
                model=booking,
                data=dict(loyalty_point_amount=payload.booking.point_amount),
            )
            self.logger.info(f"Updated booking loyalty points  - {updated_booking.loyalty_point_amount}")


