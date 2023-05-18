from tortoise import Model
from typing import Optional, Any
from tortoise.contrib.pydantic import pydantic_model_creator
from tortoise.exceptions import NoValuesFetched


class BookingLogMixin(object):
    """
    Миксин для логирования
    """

    def generate_log(
        self, use_case: str, booking_before: Optional[Model] = None, content: Optional[str] = None
    ) -> None:
        booking_id = None
        if booking_before:
            try:
                state_before: dict[str, Any] = (
                    pydantic_model_creator(booking_before.__class__).from_orm(booking_before).dict()
                )
            except NoValuesFetched:
                state_before: dict = dict()
            booking_id: int = booking_before.id
        else:
            state_before: dict = dict()
        booking_after, response_data, error_data = yield
        if booking_after:
            try:
                state_after: dict[str, Any] = (
                    pydantic_model_creator(booking_after.__class__).from_orm(booking_after).dict()
                )
            except NoValuesFetched:
                state_after: dict = dict()
            booking_id: int = booking_after.id
        else:
            state_after: dict = dict()

        log_data: dict[str, Any] = dict(
            state_before=state_before,
            state_after=state_after,
            content=content,
            booking_id=booking_id,
            response_data=response_data,
            use_case=use_case,
            error_data=error_data,
        )
        if self.create_booking_log_task:
            self.create_booking_log_task.delay(log_data=log_data)
