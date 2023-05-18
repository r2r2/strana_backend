from typing import Any, Type, Optional

from src.booking.entities import BaseBookingCase
from src.booking.exceptions import BookingNotFoundError
from src.booking.repos import Booking
from src.users.repos import CheckRepo
from src.users.types import UserBookingRepo
from src.users.repos import User
from src.task_management.utils import build_task_data

from ..types import UserAgentRepo
from ...amocrm.repos import AmocrmStatus, AmocrmStatusRepo


class UserBookingRetrieveCase(BaseBookingCase):
    """
    Кейс карточки бронирования
    """

    def __init__(
        self,
        check_repo: Type[CheckRepo],
        booking_repo: Type[UserBookingRepo],
        amocrm_status_repo: Type[AmocrmStatusRepo],
        agent_repo: Type[UserAgentRepo],
    ) -> None:
        self.check_repo: CheckRepo = check_repo()
        self.booking_repo: UserBookingRepo = booking_repo()
        self.amocrm_status_repo: AmocrmStatusRepo = amocrm_status_repo()
        self.agent_repo: UserAgentRepo = agent_repo()

    async def __call__(
        self,
        booking_id: int,
        agent_id: Optional[int] = None,
        agency_id: Optional[int] = None,
    ) -> Booking:

        if agent_id:
            filters: dict[str, Any] = dict(id=booking_id, agent_id=agent_id)
        elif agency_id:
            repres: User = await self.agent_repo.retrieve(filters=dict(id=agency_id), related_fields=["agency"])
            filters: dict[str, Any] = dict(id=booking_id, agency_id=repres.agency.id)
        else:
            filters: dict[str, Any] = dict(id=booking_id)

        prefetch_fields: list = [
            "agent",
            "agency",
            "user",
            "project",
            "building",
            "property",
            "property__floor",
            "amocrm_status",
            "task_instances",
            "task_instances__status",
            "task_instances__status__button",
            "task_instances__status__tasks_chain__task_visibility",
        ]

        booking: Booking = await self.booking_repo.retrieve(
            filters=filters,
            prefetch_fields=prefetch_fields,
        )
        if not booking:
            raise BookingNotFoundError

        if booking.project and booking.amocrm_status:
            statuses_filters: dict = dict(pipeline_id=booking.project.amo_pipeline_id)
            statuses: list[AmocrmStatus] = await self.amocrm_status_repo.list(filters=statuses_filters, ordering="sort")
            booking.amocrm_status.steps_numbers = len(statuses) + 1
            statuses.append(booking.amocrm_status)
            booking.amocrm_status.current_step = statuses.index(booking.amocrm_status) + 1
            booking.amocrm_status.actions = await booking.amocrm_status.amocrm_actions

        status = await self.check_repo.list(filters=dict(user_id=booking.user.id), ordering="-requested").first()
        booking.user.status = status
        booking.tasks = build_task_data(booking.task_instances, booking_status=booking.amocrm_status)  # type: ignore
        return booking
