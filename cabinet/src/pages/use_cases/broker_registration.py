from typing import Type, Any

from ..entities import BasePageCase
from ..repos import BrokerRegistrationRepo, BrokerRegistration


class BrokerRegistrationRetrieveCase(BasePageCase):
    """
    Страница регистрации брокера
    """

    def __init__(self, broker_registration_repo: Type[BrokerRegistrationRepo]) -> None:
        self.broker_registration_repo: BrokerRegistrationRepo = broker_registration_repo()

    async def __call__(self) -> BrokerRegistration:
        filters: dict[str, Any] = dict()
        broker_registration: BrokerRegistration = await self.broker_registration_repo.retrieve(
            filters=filters
        )
        return broker_registration
