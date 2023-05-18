import random
import string

from typing import Type

from ..entities import BaseBookingService
from ..repos import Booking, BookingRepo


class GenerateOnlinePurchaseIDService(BaseBookingService):
    """Сервис генерации уникального ID онлайн-покупки, которого точно нет в БД."""

    def __init__(self, booking_repo: Type[BookingRepo]) -> None:
        self.booking_repo: BookingRepo = booking_repo()

    async def __call__(self) -> str:
        online_purchase_id = self._generate_random_id()

        filters = dict(online_purchase_id=online_purchase_id)
        while await self.booking_repo.exists(filters):
            online_purchase_id = self._generate_random_id()
            filters = dict(online_purchase_id=online_purchase_id)

        return online_purchase_id

    @staticmethod
    def _generate_random_id() -> str:
        """Генерация строки по шаблону '00-AA-000'."""
        return "".join(
            (
                random.choice(string.digits),
                random.choice(string.digits),
                "-",
                random.choice(string.ascii_uppercase),
                random.choice(string.ascii_uppercase),
                "-",
                random.choice(string.digits),
                random.choice(string.digits),
                random.choice(string.digits),
            )
        )
