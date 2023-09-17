import structlog
from http import HTTPStatus
from typing import Type, Any
from fastapi import HTTPException

from common.settings.repos import BookingSettingsRepo
from src.users.repos import User, UserRepo
from src.booking.repos import Booking
from src.users.constants import UserType
from src.users.repos import CheckRepo, UserPinningStatus, UserPinningStatusRepo
from src.task_management.utils import is_task_in_compare_task_chain, TaskDataBuilder
from src.amocrm.repos import AmocrmGroupStatusRepo, AmocrmGroupStatus

from ..entities import BaseMeetingCase
from ..repos import Meeting, MeetingRepo, MeetingStatusRepo
from ..exceptions import MeetingNotFoundError
from src.task_management.repos import TaskInstance
from src.task_management.constants import MeetingsSlug


class MeetingsDetailCase(BaseMeetingCase):
    """
    Кейс для деталки встреч.
    """
    def __init__(
        self,
        meeting_repo: Type[MeetingRepo],
        meeting_status_repo: Type[MeetingStatusRepo],
        booking_settings_repo: Type[BookingSettingsRepo],
        user_repo: Type[UserRepo],
        amocrm_group_status_repo: Type[AmocrmGroupStatusRepo],
        check_repo: Type[CheckRepo],
        user_pinning_repo: Type[UserPinningStatusRepo],
    ) -> None:
        self.meeting_repo: MeetingRepo = meeting_repo()
        self.meeting_status_repo = meeting_status_repo()
        self.user_repo: UserRepo = user_repo()
        self.booking_settings_repo: BookingSettingsRepo = booking_settings_repo()
        self.amocrm_group_status_repo: AmocrmGroupStatusRepo = amocrm_group_status_repo()
        self.check_repo: CheckRepo = check_repo()
        self.user_pinning_repo: UserPinningStatusRepo = user_pinning_repo()
        self.logger = structlog.getLogger(__name__)

    async def __call__(
        self,
        *,
        meeting_id: int,
        user_id: int,
    ) -> Meeting:
        meeting: Meeting = await self.meeting_repo.retrieve(
            filters=dict(id=meeting_id),
            prefetch_fields=[
                "status",
                "booking__amocrm_status__group_status",
                "booking__user",
                "booking__agent",
                "booking__agency",
                "booking__property__floor",
                "booking__task_instances__status__buttons",
                "booking__task_instances__status__tasks_chain__task_visibility",
            ],
            ordering="date",
        )
        if not meeting:
            raise MeetingNotFoundError

        user: User = await self.user_repo.retrieve(filters=dict(id=user_id))
        if (user.type == UserType.CLIENT and meeting.booking.user_id != user.id) or (
            user.type in [UserType.AGENT, UserType.REPRES] and meeting.booking.agent_id != user.id
        ):
            raise HTTPException(
                status_code=HTTPStatus.FORBIDDEN,
                detail="Not authenticated",
                headers={"WWW-Authenticate": "Bearer"},
            )

        # находим текущий шаг и количество шагов по статусу встречи
        meeting_statuses: list[MeetingStatusRepo] = await self.meeting_status_repo.list(filters=dict(is_final=False))
        final_meeting_statuses_ids: list[MeetingStatusRepo] = await self.meeting_status_repo.list(
            filters=dict(is_final=True)
        ).values_list("id", flat=True)
        if meeting.status_id in final_meeting_statuses_ids:
            meeting.current_step = meeting.steps_numbers = len(meeting_statuses) + 1
        else:
            for number, meeting_status in enumerate(meeting_statuses):
                if meeting_status.id == meeting.status_id:
                    meeting.current_step = number + 1
                    meeting.steps_numbers = len(meeting_statuses) + 1
                    break

        # получаем данные для расширенной информации и сделке
        group_statuses: list[AmocrmGroupStatus] = await self.amocrm_group_status_repo.list(
            filters=dict(is_final=False),
            ordering="sort",
        )
        final_group_statuses: list[AmocrmGroupStatus] = await self.amocrm_group_status_repo.list(
            filters=dict(is_final=True),
        )
        final_group_statuses_ids = [final_group_status.id for final_group_status in final_group_statuses]
        booking_group_status = meeting.booking.amocrm_status.group_status
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
            meeting.booking.amocrm_status.name = booking_group_status.name
            meeting.booking.amocrm_status.group_id = booking_group_status.id
            meeting.booking.amocrm_status.show_reservation_date = booking_group_status.show_reservation_date
            meeting.booking.amocrm_status.show_booking_date = booking_group_status.show_booking_date

        meeting.booking.amocrm_status.color = booking_group_status.color if booking_group_status else None
        meeting.booking.amocrm_status.steps_numbers = len(group_statuses) + 1
        meeting.booking.amocrm_status.current_step = booking_group_status_current_step
        meeting.booking.amocrm_status.actions = booking_group_status_actions

        status = await self.check_repo.list(
            filters=dict(user_id=meeting.booking.user.id),
            ordering="-requested",
            related_fields=["unique_status"],
        ).first()
        pinning_status: UserPinningStatus = await self.user_pinning_repo.retrieve(
            filters=dict(user_id=meeting.booking.user.id),
            related_fields=["unique_status"],
        )
        meeting.booking.user.status = status
        meeting.booking.user.pinning_status = pinning_status
        meeting.booking.tasks = await self.get_meeting_tasks(
            task_instances=meeting.booking.task_instances,
            booking=meeting.booking,
        )

        return meeting

    async def get_meeting_tasks(
        self,
        task_instances: list[TaskInstance],
        booking: Booking,
    ) -> list[dict[str, Any]]:
        """
        Получение только задач встречи
        """
        meeting_tasks = [
            task_instance for task_instance in task_instances
            if await is_task_in_compare_task_chain(
                status=task_instance.status, compare_status=MeetingsSlug.SIGN_UP.value
            )
        ]

        sorted_meeting_tasks = sorted(
            meeting_tasks,
            key=lambda x: x.status.priority,
        )

        booking_settings = await self.booking_settings_repo.list().first()
        return await TaskDataBuilder(
            task_instances=sorted_meeting_tasks,
            booking=booking,
            booking_settings=booking_settings,
        ).build()


