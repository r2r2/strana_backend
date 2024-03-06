from typing import Any

from common.settings.constants import SystemListSlug
from common.settings.repos import BookingSettingsRepo, SystemList, BookingSettings
from common.settings.utils import get_system_by_slug
from src.booking.entities import BaseBookingCase
from src.booking.exceptions import BookingNotFoundError
from src.booking.repos import Booking, BookingTagRepo, BookingTag
from src.users.repos import CheckRepo, UserPinningStatus, UserPinningStatusRepo
from src.users.types import UserBookingRepo
from src.users.repos import User
from src.projects.constants import ProjectStatus
from src.task_management.utils import TaskDataBuilder
from src.task_management.constants import BOOKING_UPDATE_FIXATION_STATUSES

from ..types import UserAgentRepo
from ...amocrm.repos import AmocrmGroupStatusRepo, AmocrmGroupStatus
from src.task_management.repos import TaskInstance


class UserBookingRetrieveCase(BaseBookingCase):
    """
    Кейс карточки бронирования
    """

    def __init__(
        self,
        check_repo: type[CheckRepo],
        booking_repo: type[UserBookingRepo],
        booking_settings_repo: type[BookingSettingsRepo],
        amocrm_group_status_repo: type[AmocrmGroupStatusRepo],
        agent_repo: type[UserAgentRepo],
        user_pinning_repo: type[UserPinningStatusRepo],
        booking_tag_repo: type[BookingTagRepo],
    ) -> None:
        self.check_repo: CheckRepo = check_repo()
        self.booking_repo: UserBookingRepo = booking_repo()
        self.booking_settings_repo: BookingSettingsRepo = booking_settings_repo()
        self.amocrm_group_status_repo: AmocrmGroupStatusRepo = (
            amocrm_group_status_repo()
        )
        self.agent_repo: UserAgentRepo = agent_repo()
        self.user_pinning_repo: UserPinningStatusRepo = user_pinning_repo()
        self.booking_tag_repo: BookingTagRepo = booking_tag_repo()

    async def __call__(
        self,
        booking_id: int,
        agent_id: int | None = None,
        agency_id: int | None = None,
    ) -> Booking:
        if agent_id:
            filters: dict[str, Any] = dict(id=booking_id, agent_id=agent_id)
        elif agency_id:
            repres: User = await self.agent_repo.retrieve(
                filters=dict(id=agency_id), related_fields=["agency"]
            )
            filters: dict[str, Any] = dict(id=booking_id, agency_id=repres.agency.id)
        else:
            filters: dict[str, Any] = dict(id=booking_id)

        prefetch_fields: list = [
            "agent",
            "agency",
            "user",
            "project__city",
            "building",
            "property__section",
            "property__property_type",
            "property__floor",
            "amocrm_status__group_status",
            "task_instances__status__buttons",
            "task_instances__status__tasks_chain__task_visibility",
            "task_instances__status__tasks_chain__systems",
            "amo_payment_method",
            "mortgage_type",
        ]

        booking: Booking = await self.booking_repo.retrieve(
            filters=filters,
            prefetch_fields=prefetch_fields,
        )
        if not booking:
            raise BookingNotFoundError

        booking.show_update_fixation_info = False
        if booking.amocrm_status:
            await self._set_group_statuses(booking=booking)
            if (
                booking.amocrm_status.group_status
                and booking.amocrm_status.group_status.name in BOOKING_UPDATE_FIXATION_STATUSES
            ):
                booking.show_update_fixation_info = True

        booking.booking_tags = await self._get_booking_tags(booking)
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

        if booking.project and booking.project.status == ProjectStatus.FUTURE:
            booking.tasks = None
        else:
            booking.tasks = await self._get_booking_tasks(booking=booking)

        booking: Booking = await self._deactivated_booking_response(booking=booking)

        return booking

    async def _get_booking_tags(self, booking: Booking) -> list[BookingTag] | None:
        tag_filters: dict[str, Any] = dict(
            is_active=True,
            group_statuses=booking.amocrm_status.group_status
            if booking.amocrm_status else None,
        )
        return (
            await self.booking_tag_repo.list(filters=tag_filters, ordering="-priority")
        ) or None

    async def _deactivated_booking_response(self, booking: Booking) -> Booking:
        if not booking.active:
            booking.property = booking.building = booking.expires = None
            return booking
        return booking

    async def _set_group_statuses(self, booking: Booking) -> None:
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

        booking_group_status_actions = (
            await booking_group_status.amocrm_actions if booking_group_status else None
        )

        if booking_group_status:
            booking.amocrm_status.name = booking_group_status.name
            booking.amocrm_status.group_id = booking_group_status.id
            booking.amocrm_status.show_reservation_date = (
                booking_group_status.show_reservation_date
            )
            booking.amocrm_status.show_booking_date = (
                booking_group_status.show_booking_date
            )

        booking.amocrm_status.color = (
            booking_group_status.color if booking_group_status else None
        )
        booking.amocrm_status.steps_numbers = len(group_statuses) + 1
        booking.amocrm_status.current_step = booking_group_status_current_step
        booking.amocrm_status.actions = booking_group_status_actions

    async def _get_booking_tasks(self, booking: Booking) -> list[dict[str, Any] | None]:
        booking_settings: BookingSettings = await self.booking_settings_repo.list().first()
        broker_system: SystemList = await get_system_by_slug(SystemListSlug.LK_BROKER.value)
        task_instances: list[TaskInstance] = sorted(booking.task_instances, key=lambda x: x.status.priority)
        task_instances: list[TaskInstance] = list(filter(
            lambda task: broker_system in task.status.tasks_chain.systems,
            task_instances,
        ))

        tasks: list[dict[str, Any] | None] = await TaskDataBuilder(
            task_instances=task_instances,
            booking=booking,
            booking_settings=booking_settings,
        ).build()
        return tasks
