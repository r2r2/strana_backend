import json
from asyncio import create_task

from common.loggers.utils import get_difference_between_two_dicts, dumps_dict
from ..repos import Booking, BookingRepo
from ..entities import BaseBookingCase


def booking_changes_logger(booking_change: BookingRepo(), use_case: BaseBookingCase, content: str):
    from src.booking.tasks import create_booking_log_task_v2
    """
    Логирование изменений бронирования
    """

    async def _wrapper(booking: Booking = None, data: dict = None, filters: dict = None, exclude_filters: dict = None):
        booking_after, response_data = dict(), dict()
        booking_before: str = dumps_dict(dict(booking)) if booking else dict()
        booking_difference_json: str = ""
        error_data, booking_id = None, None

        if data and filters:
            if not exclude_filters:
                update_booking = booking_change(filters=filters, data=data)
            else:
                update_booking = booking_change(filters=filters, data=data, exclude_filters=exclude_filters)
        elif booking and isinstance(data, dict):
            update_booking = booking_change(model=booking, data=data)
        elif booking:
            update_booking = booking_change(model=booking)
        else:
            update_booking = booking_change(data=data)

        try:
            booking: Booking = await update_booking
            booking_id: int = booking.id if booking else None
            booking_after: str = dumps_dict(
                dict(booking)
            ) if booking else dict()
            booking_difference: dict = get_difference_between_two_dicts(
                json.loads(booking_before), json.loads(booking_after)
            )
            booking_difference_json: str = json.dumps(booking_difference, indent=4, sort_keys=True, default=str)
        except Exception as error:
            error_data = str(error)


        log_data: dict = dict(
            state_before=booking_before,
            state_after=booking_after,
            state_difference=booking_difference_json,
            content=content,
            booking_id=booking_id,
            response_data=response_data,
            use_case=use_case.__class__.__name__,
            error_data=error_data,
        )
        create_task(create_booking_log_task_v2(log_data=log_data))

        return booking

    return _wrapper
