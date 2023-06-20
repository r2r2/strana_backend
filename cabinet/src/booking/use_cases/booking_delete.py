from typing import Any, Type, Callable, Union

from ..constants import BookingSubstages, BookingStages
from ..decorators import logged_action
from ..entities import BaseBookingCase
from ..exceptions import BookingWrongStepError, BookingNotFoundError
from ..mixins import BookingLogMixin
from ..repos import BookingRepo, Booking
from ..types import BookingSqlUpdateRequest, BookingProfitBase, BookingAmoCRM, BookingPropertyRepo
from ..loggers.wrappers import booking_changes_logger


class BookingDeleteCase(BaseBookingCase, BookingLogMixin):
    """
    Удаление бронирования
    """

    def __init__(
        self,
        create_booking_log_task: Any,
        backend_config: dict[str, Any],
        booking_repo: Type[BookingRepo],
        amocrm_class: Type[BookingAmoCRM],
        property_repo: Type[BookingPropertyRepo],
        profitbase_class: Type[BookingProfitBase],
        request_class: Type[BookingSqlUpdateRequest],
        global_id_decoder: Callable[[str], tuple[str, Union[str, int]]],
    ) -> None:
        self.booking_repo: BookingRepo = booking_repo()
        self.property_repo: BookingPropertyRepo = property_repo()

        self.amocrm_class: Type[BookingAmoCRM] = amocrm_class
        self.create_booking_log_task: Any = create_booking_log_task
        self.profitbase_class: Type[BookingProfitBase] = profitbase_class
        self.request_class: Type[BookingSqlUpdateRequest] = request_class
        self.global_id_decoder: Callable[[str], tuple[str, Union[str, int]]] = global_id_decoder
        self.booking_update = booking_changes_logger(self.booking_repo.update, self, content="Разбронирование| AMOCRM")

        self.connection_options: dict[str, Any] = dict(
            user=backend_config["db_user"],
            host=backend_config["db_host"],
            port=backend_config["db_port"],
            database=backend_config["db_name"],
            password=backend_config["db_password"],
        )

    async def __call__(self, user_id: int, booking_id: int) -> Booking:
        filters: dict[str, Any] = dict(id=booking_id, user_id=user_id, active=True)
        booking: Booking = await self.booking_repo.retrieve(
            filters=filters, related_fields=["user", "project", "project__city", "property", "building"]
        )
        if not booking:
            raise BookingNotFoundError
        if booking.step_four():
            raise BookingWrongStepError
        data: dict[str, Any] = dict(active=False)
        property_data: dict[str, Any] = dict(status=booking.property.statuses.FREE)
        if booking.step_two():
            extra_data: dict[str, Any] = dict(
                active=False,
                profitbase_booked=False,
                amocrm_stage=BookingStages.DDU_UNREGISTERED,
                amocrm_substage=BookingSubstages.UNREALIZED,
            )
            data.update(extra_data)
            await self._profitbase_unbooking(booking=booking)
            await self._amocrm_unbooking(booking=booking)
        await self._backend_unbooking(booking=booking)
        await self.booking_update(booking=booking, data=data)
        await self.property_repo.update(booking.property, data=property_data)
        return booking

    # @logged_action(content="РАЗБРОНИРОВАНИЕ | AMOCRM")
    async def _amocrm_unbooking(self, booking: Booking) -> int:
        async with await self.amocrm_class() as amocrm:
            lead_options: dict[str, Any] = dict(
                status=BookingSubstages.UNREALIZED,
                lead_id=booking.amocrm_id,
                city_slug=booking.project.city.slug,
            )
            data: list[Any] = await amocrm.update_lead(**lead_options)
            lead_id: int = data[0]["id"]
        return lead_id

    # @logged_action(content="РАЗБРОНИРОВАНИЕ | PROFITBASE")
    async def _profitbase_unbooking(self, booking: Booking) -> bool:
        async with await self.profitbase_class() as profitbase:
            data: dict[str, bool] = await profitbase.unbook_property(deal_id=booking.amocrm_id)
        success: bool = data["success"]
        return success

    # @logged_action(content="РАЗБРОНИРОВАНИЕ | PORTAL")
    async def _backend_unbooking(self, booking: Booking) -> str:
        _, property_id = self.global_id_decoder(global_id=booking.property.global_id)
        request_options: dict[str, Any] = dict(
            table="properties_property",
            filters=dict(id=property_id),
            data=dict(status=booking.property.statuses.FREE),
            connection_options=self.connection_options,
        )
        async with self.request_class(**request_options) as response:
            result: str = response
        return result
