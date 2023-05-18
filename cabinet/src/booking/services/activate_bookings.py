import json
from typing import Any

from ..constants import BookingSubstages
from ..repos import Booking
from ..types import BookingProperty, WebhookLead
from .base_booking import BaseBookingsService


class ActivateBookingsService(BaseBookingsService):
    """
    Кейс активации бронирования
    """
    async def __call__(
            self,
            booking: Booking,
            webhook_lead: WebhookLead,
            property_final_price: int,
            price_with_sale: int,
            amocrm_substage: str
    ):
        data: dict[str] = dict(active=True)
        booking = await self.booking_repo.update(booking, data=data)
        filters: dict[str] = dict(id=booking.property_id)
        booking_property: BookingProperty = await self.property_repo.retrieve(filters=filters)
        if booking_property:
            data: dict[str, Any] = {}
            if property_final_price or price_with_sale:
                data.update(final_price=property_final_price or price_with_sale)
            data.update(status=booking_property.statuses.BOOKED)
            if amocrm_substage in {BookingSubstages.MONEY_PROCESS, BookingSubstages.REALIZED}:
                data.update(status=booking_property.statuses.SOLD)
            await self.property_repo.update(booking_property, data=data)
            setattr(booking, "property", booking_property)
            await self._backend_booking(booking=booking)
        await self.webhook_request_repo.create(
            data=dict(
                category="booking_activation",
                body=json.dumps(
                    dict(
                        lead_id=webhook_lead.lead_id,
                        new_status_id=webhook_lead.new_status_id,
                        custom_fields=webhook_lead.custom_fields,
                        webhook_data=json.dumps(data),
                    )
                ),
            )
        )
        self.logger.info('Amocrm booking activated', booking=booking.id, amocrm_id=booking.amocrm_id)

    async def _backend_booking(self, booking: Booking) -> bool:
        """
        send booked property to backend
        """
        book_options: dict[str, Any] = dict(
            login=self.login,
            url=self.backend_url,
            type=self.query_type,
            password=self.password,
            query_name=self.query_name,
            query_directory=self.query_directory,
            filters=(booking.property.global_id, booking.property.status),
        )
        async with self.request_class(**book_options) as response:
            response_ok: bool = response.ok
        return response_ok
