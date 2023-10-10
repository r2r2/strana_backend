from src.booking.repos import PaymentPageNotificationRepo, PaymentPageNotification
from src.notifications.entities import BaseNotificationCase
from src.notifications.exceptions import PaymentPageNotificationNotFoundError


class PaymentPageCase(BaseNotificationCase):
    def __init__(
        self,
        payment_page_repo: type[PaymentPageNotificationRepo],
    ):
        self.payment_page_repo: PaymentPageNotificationRepo = payment_page_repo()

    async def __call__(self, slug: str) -> PaymentPageNotification:
        template: PaymentPageNotification = await self.payment_page_repo.retrieve(
            filters=dict(slug=slug)
        )
        if not template:
            raise PaymentPageNotificationNotFoundError
        return template
