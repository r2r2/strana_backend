from typing import Optional

from src.booking.exceptions import BookingNotFoundError
from src.booking.repos import BookingRepo, Booking
from src.task_management.dto import UpdateTaskDTO
from src.task_management.entities import BaseTaskCase
from src.task_management.services import UpdateTaskInstanceStatusService


class AmoCRMWebhookUpdateTaskInstanceCase(BaseTaskCase):
    """
    Обновление статуса задания из вебхука АМО
    """

    def __init__(
        self,
        booking_repo: type[BookingRepo],
        update_task_instance_status_service: UpdateTaskInstanceStatusService,
    ):
        self.booking_repo = booking_repo()
        self.update_task_instance_status_service: UpdateTaskInstanceStatusService = update_task_instance_status_service

    async def __call__(self, data: dict[str, list[str]]) -> None:
        booking_amocrm_id: int = int(data.get('id')[0])
        slug: str = data.get('result_status')[0]
        comment: Optional[str] = data.get('comment')[0] if data.get('comment') else None

        booking: Booking = await self.booking_repo.retrieve(filters=dict(amocrm_id=booking_amocrm_id))
        if not booking:
            raise BookingNotFoundError

        task_context: UpdateTaskDTO = UpdateTaskDTO()
        task_context.comment = comment

        await self.update_task_instance_status_service(
            booking_id=booking.id,
            status_slug=slug,  # "И в вебхуке будем двигать на тот слаг статуса, какой они присылают"© Игорь Рыбаков
            task_context=task_context,
        )
