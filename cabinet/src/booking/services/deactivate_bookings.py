import json
from typing import Any

from .base_booking import BaseBookingsService
from ..repos import Booking
from ..types import BookingProperty, WebhookLead


class DeactivateBookingsService(BaseBookingsService):
    """
    Кейс деактивации бронирования
    """
    async def __call__(self, booking: Booking, webhook_lead: WebhookLead, stages_valid: bool):
        data: dict[str] = dict(active=False)
        booking: Booking = await self.booking_repo.update(booking, data=data)
        filters: dict[str] = dict(id=booking.property_id)
        booking_property: BookingProperty = await self.property_repo.retrieve(filters=filters)
        if booking_property:
            data: dict[str] = dict(status=booking_property.statuses.FREE)
            await self.property_repo.update(booking_property, data=data)
            setattr(booking, "property", booking_property)
            await self._backend_unbooking(booking=booking)

        await self.webhook_request_repo.create(
            data=dict(
                category="booking_deactivation",
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
        self.logger.info(
            'Amocrm booking deactivated',
            booking_id=booking.id,
            property_id=booking.property_id,
            stages_valid=stages_valid,
            amocrm_id=booking.amocrm_id,
        )
        if self.check_pinning is not None:
            self.check_pinning.as_task(user_id=booking.user_id)

    async def _backend_unbooking(self, booking: Booking) -> bool:
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
            filters=(booking.property.global_id, booking.property.status),
        )
        async with self.request_class(**unbook_options) as response:
            response_ok: bool = response.ok
        return response_ok
