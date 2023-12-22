import asyncio

from common.amocrm.components import AmoCRMLeads
from ..loggers import booking_changes_logger
from ..repos import Booking
from ..types import BookingProperty
from typing import Type, Any
from ..entities import BaseBookingService
from ..constants import BookingSubstages
from ..types import BookingAmoCRM, BookingProfitBase
from ..repos import BookingRepo
from ..types import BookingPropertyRepo
from config import backend_config
from common.requests import GraphQLRequest
from src.properties.constants import PropertyStatuses


class DeactivateBookingService(BaseBookingService):
    """
    Кейс деактивации бронирования
    """

    query_type: str = "changePropertyStatus"
    query_name: str = "changePropertyStatus.graphql"
    query_directory: str = "/src/booking/queries/"

    def __init__(
        self,
        amocrm_class: Type[BookingAmoCRM],
        profitbase_class: Type[BookingProfitBase],
        booking_repo: Type[BookingRepo],
        property_repo: Type[BookingPropertyRepo],
        request_class: Type[GraphQLRequest],
    ) -> None:
        self.amocrm_class: Type[BookingAmoCRM] = amocrm_class
        self.profitbase_class: Type[BookingProfitBase] = profitbase_class
        self.booking_repo: BookingRepo = booking_repo()
        self.property_repo: BookingPropertyRepo = property_repo()
        self.login: str = backend_config["internal_login"]
        self.password: str = backend_config["internal_password"]
        self.backend_url: str = backend_config["url"] + backend_config["graphql"]
        self.request_class: Type[GraphQLRequest] = request_class
        self.booking_update = booking_changes_logger(
            self.booking_repo.update, self, content="ДЕАКТИВАЦИЯ БРОНИ | AMOCRM, PORTAL, PROFITBASE"
        )

    async def __call__(self, booking: Booking) -> None:
        data: dict[str] = dict(active=False)
        booking: Booking = await self.booking_update(booking=booking, data=data)
        filters: dict[str] = dict(id=booking.property_id)
        booking_property: BookingProperty = await self.property_repo.retrieve(filters=filters)
        if booking_property:
            data: dict[str] = dict(status=PropertyStatuses.FREE)
            await self.property_repo.update(booking_property, data=data)
            setattr(booking, "property", booking_property)
            await asyncio.gather(
                self.__backend_unbooking(booking=booking),
                self.__amocrm_unbooking(booking=booking),
                self.__profitbase_unbooking(booking=booking),
            )

    # @logged_action(content="РАЗБРОНИРОВАНИЕ | PORTAL")
    async def __backend_unbooking(self, booking: Booking) -> bool:
        """
        send unbooking property to backend
        """
        unbook_options: dict[str, Any] = dict(
            login=self.login,
            url=self.backend_url,
            type=self.query_type,
            password=self.password,
            query_name=self.query_name,
            query_directory=self.query_directory,
            filters=(booking.property.global_id, PropertyStatuses.FREE),
        )
        async with self.request_class(**unbook_options) as response:
            response_ok: bool = response.ok
        return response_ok

    # @logged_action(content="РАЗБРОНИРОВАНИЕ | AMOCRM")
    async def __amocrm_unbooking(self, booking: Booking) -> int:
        await booking.fetch_related("project", "project__city")
        async with await self.amocrm_class() as amocrm:
            lead_options: dict[str, Any] = dict(
                status=BookingSubstages.MAKE_DECISION,
                lead_id=booking.amocrm_id,
                city_slug=booking.project.city.slug,
            )
            data: list[Any] = await amocrm.update_lead(**lead_options)
            lead_id: int = data[0]["id"]
        return lead_id

    # @logged_action(content="РАЗБРОНИРОВАНИЕ | PROFITBASE")
    async def __profitbase_unbooking(self, booking: Booking) -> bool:
        async with await self.profitbase_class() as profitbase:
            data: dict[str, bool] = await profitbase.unbook_property(deal_id=booking.amocrm_id)
        success: bool = data["success"]
        return success
