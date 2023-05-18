from typing import Any, Optional

from src.booking.exceptions import BookingNotFoundError
from src.booking.repos import BookingRepo, Booking
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

    async def __call__(self, data: dict[str, Any]) -> None:
        booking_amocrm_id: int = data.get('id')
        slug: str = data.get('result_status')
        comment: Optional[str] = data.get('comment')

        booking: Booking = await self.booking_repo.retrieve(filters=dict(amocrm_id=booking_amocrm_id))
        if not booking:
            raise BookingNotFoundError

        await self.update_task_instance_status_service(
            booking_id=booking.id,
            status_slug=slug,  # "И в вебхуке будем двигать на тот слаг статуса, какой они присылают"© Игорь Рыбаков
            comment=comment,
        )
