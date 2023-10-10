from datetime import datetime

from src.task_management.entities import BaseTaskContextDTO


class CreateTaskDTO(BaseTaskContextDTO):
    status_slug: str | None
    meeting_new_date: datetime | None
    booking_created: bool = False


class UpdateTaskDTO(BaseTaskContextDTO):
    comment: str | None
    by_button: bool = False
