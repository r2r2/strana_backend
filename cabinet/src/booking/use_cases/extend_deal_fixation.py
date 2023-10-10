from http import HTTPStatus
from fastapi import HTTPException
from datetime import datetime
from pytz import UTC

from src.booking.repos import BookingRepo, Booking
from src.users.repos import UserRepo, User
from src.users.constants import UserType
from src.task_management.services import UpdateTaskInstanceStatusService
from src.task_management.constants import FixationExtensionSlug, BOOKING_UPDATE_FIXATION_STATUSES
from ..entities import BaseBookingCase
from ..exceptions import BookingNotFoundError, BookingHasNoCorrectFixationTaskError
from src.task_management.dto import UpdateTaskDTO


class ExtendDeaFixationCase(BaseBookingCase):
    """
    Продление фиксации клиента в сделке.
    """

    def __init__(
        self,
        booking_repo: type[BookingRepo],
        user_repo: type[UserRepo],
        update_task_instance_service: UpdateTaskInstanceStatusService,
    ) -> None:
        self.booking_repo: BookingRepo = booking_repo()
        self.user_repo: UserRepo = user_repo()
        self.update_task_instance_service: UpdateTaskInstanceStatusService = update_task_instance_service

    async def __call__(
        self,
        booking_id: int,
        user_id: int,
    ) -> None:
        user: User = await self.user_repo.retrieve(filters=dict(id=user_id))
        if user.type not in [UserType.AGENT, UserType.REPRES]:
            raise HTTPException(
                status_code=HTTPStatus.FORBIDDEN,
                detail="Not authenticated",
                headers={"WWW-Authenticate": "Bearer"},
            )

        booking: Booking = await self.booking_repo.retrieve(
            filters=dict(id=booking_id),
            prefetch_fields=[
                "task_instances",
                "task_instances__status",
                "amocrm_status",
                "amocrm_status__group_status",
            ],
        )
        if not booking or booking.agent_id != user.id:
            raise BookingNotFoundError

        booking_has_correct_task = False
        status_slug = None
        for task_instance in booking.task_instances:
            if task_instance.status.slug == FixationExtensionSlug.DEAL_NEED_EXTENSION.value:
                booking_has_correct_task = True
                if (
                    booking.amocrm_status
                    and booking.amocrm_status.group_status
                    and booking.amocrm_status.group_status.name not in BOOKING_UPDATE_FIXATION_STATUSES
                ):
                    status_slug = FixationExtensionSlug.DEAL_ALREADY_BOOKED.value
                elif booking.extension_number < 1:
                    status_slug = FixationExtensionSlug.CANT_EXTEND_DEAL_BY_ATTEMPT.value
                elif booking.fixation_expires < datetime.now(tz=UTC):
                    status_slug = FixationExtensionSlug.CANT_EXTEND_DEAL_BY_DATE.value
                else:
                    status_slug = FixationExtensionSlug.NO_EXTENSION_NEEDED.value
                break

        if not booking_has_correct_task:
            raise BookingHasNoCorrectFixationTaskError

        task_context: UpdateTaskDTO = UpdateTaskDTO()
        task_context.by_button = True
        await self.update_task_instance_service(
            booking_id=booking_id,
            status_slug=status_slug,
            task_context=task_context,
        )
