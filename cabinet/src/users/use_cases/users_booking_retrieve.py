from typing import Any, Type, Optional

from common.settings.repos import BookingSettingsRepo
from src.booking.entities import BaseBookingCase
from src.booking.exceptions import BookingNotFoundError
from src.booking.repos import Booking
from src.users.repos import CheckRepo, UserPinningStatus, UserPinningStatusRepo
from src.users.types import UserBookingRepo
from src.users.repos import User
from src.task_management.utils import build_task_data

from ..types import UserAgentRepo
from ...amocrm.repos import AmocrmGroupStatusRepo, AmocrmGroupStatus


class UserBookingRetrieveCase(BaseBookingCase):
    """
    Кейс карточки бронирования
    """

    def __init__(
        self,
        check_repo: Type[CheckRepo],
        booking_repo: Type[UserBookingRepo],
        booking_settings_repo: Type[BookingSettingsRepo],
        amocrm_group_status_repo: Type[AmocrmGroupStatusRepo],
        agent_repo: Type[UserAgentRepo],
        user_pinning_repo: Type[UserPinningStatusRepo],
    ) -> None:
        self.check_repo: CheckRepo = check_repo()
        self.booking_repo: UserBookingRepo = booking_repo()
        self.booking_settings_repo: BookingSettingsRepo = booking_settings_repo()
        self.amocrm_group_status_repo: AmocrmGroupStatusRepo = amocrm_group_status_repo()
        self.agent_repo: UserAgentRepo = agent_repo()
        self.user_pinning_repo: UserPinningStatusRepo = user_pinning_repo()

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
            "project__city",
            "building",
            "property",
            "property__section",
            "property__property_type",
            "property__floor",
            "amocrm_status__group_status",
            "task_instances__status__buttons",
            "task_instances__status__tasks_chain__task_visibility",
        ]

        booking: Booking = await self.booking_repo.retrieve(
            filters=filters,
            prefetch_fields=prefetch_fields,
        )
        if not booking:
            raise BookingNotFoundError

        if booking.amocrm_status:
            group_statuses: list[AmocrmGroupStatus] = await self.amocrm_group_status_repo.list(
                filters=dict(is_final=False),
                ordering="sort",
            )
            final_group_statuses: list[AmocrmGroupStatus] = await self.amocrm_group_status_repo.list(
                filters=dict(is_final=True),
            )
            final_group_statuses_ids = [final_group_status.id for final_group_status in final_group_statuses]

            booking_group_status = booking.amocrm_status.group_status
            if not booking_group_status:
                booking_group_status_current_step = 1
            elif booking_group_status.id in final_group_statuses_ids:
                booking_group_status_current_step = len(group_statuses) + 1
            else:
                for number, group_status in enumerate(group_statuses):
                    if booking_group_status.id == group_status.id:
                        booking_group_status_current_step = number + 1

            booking_group_status_actions = await booking_group_status.amocrm_actions if booking_group_status else None

            if booking_group_status:
                booking.amocrm_status.name = booking_group_status.name
                booking.amocrm_status.group_id = booking_group_status.id
                booking.amocrm_status.show_reservation_date = booking_group_status.show_reservation_date
                booking.amocrm_status.show_booking_date = booking_group_status.show_booking_date

            booking.amocrm_status.color = booking_group_status.color if booking_group_status else None
            booking.amocrm_status.steps_numbers = len(group_statuses) + 1
            booking.amocrm_status.current_step = booking_group_status_current_step
            booking.amocrm_status.actions = booking_group_status_actions

        status = await self.check_repo.list(
            filters=dict(user_id=booking.user.id),
            ordering="-requested",
            related_fields=["unique_status"],
        ).first()
        pinning_status: UserPinningStatus = await self.user_pinning_repo.retrieve(
            filters=dict(user_id=booking.user.id),
            related_fields=["unique_status"],
        )
        booking.user.status = status
        booking.user.pinning_status = pinning_status
        task_instances = sorted(booking.task_instances, key=lambda x: x.status.priority)
        booking_settings = await self.booking_settings_repo.list().first()
        booking.tasks = await build_task_data(
            task_instances=task_instances,
            booking=booking,
            booking_settings=booking_settings,
        )
        return booking
