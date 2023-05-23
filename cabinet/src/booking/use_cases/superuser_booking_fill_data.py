from typing import Any

from config import lk_admin_config
from ..entities import BaseBookingCase


class SuperuserBookingFillDataCase(BaseBookingCase):
    """
    Обновление сделок в АмоСРМ после изменения в админке брокера.
    """

    def __init__(
        self,
        export_booking_in_amo_task: Any,
    ) -> None:
        self.export_booking_in_amo_task: Any = export_booking_in_amo_task

    def __call__(
        self,
        booking_id: int,
        data: str,
    ) -> None:

        if data == lk_admin_config["admin_export_key"]:
            self.export_booking_in_amo_task.delay(booking_id=booking_id)

