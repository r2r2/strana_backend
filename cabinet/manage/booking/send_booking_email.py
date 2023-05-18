from copy import copy
from tortoise import Tortoise
from config import tortoise_config
from common.email import EmailService
from typing import Any, Coroutine, Type
from src.booking import repos as booking_repos


class SendBookingEmail(object):
    """
    Отправка письма о бронировании
    """

    def __init__(self) -> None:
        self.booking_repo: booking_repos.BookingRepo = booking_repos.BookingRepo()
        self.orm_class: Type[Tortoise] = Tortoise
        self.orm_config: dict[str, Any] = copy(tortoise_config)
        self.orm_config.pop("generate_schemas", None)

    def __await__(self) -> Coroutine:
        return self().__await__()

    async def __call__(self, *args, **kwargs) -> None:
        await self.orm_class.init(config=self.orm_config)
        filters: dict[str, Any] = dict(user__email="bb@idaproject.com")
        booking: booking_repos.Booking = await self.booking_repo.retrieve(
            filters=filters, related_fields=["user", "project", "property", "building", "floor"]
        )
        resources: dict[str, Any] = dict(
            topic="ТЕСТ: Успешная оплата бронирования",
            recipients=[booking.user.email],
            template="src/booking/templates/success_booking.html",
            context=dict(booking=booking),
        )
        email_service: EmailService = EmailService(**resources)
        await email_service()
        await self.orm_class.close_connections()
