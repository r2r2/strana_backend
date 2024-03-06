import structlog
from typing import Type
from asyncio import create_task

from common.unleash.client import UnleashClient
from config.feature_flags import FeatureFlags
from src.users.entities import BaseUserCase
from src.agents.services import ImportClientsService, ImportClientsAllBookingService
from src.users.repos import User, UserRepo
from src.users.exceptions import UserWasDeletedError

from ..models import RequestImportClientsAndBookingsModel


class ImportClientsAndBookingsModelCase(BaseUserCase):
    """
    Ручной запуск сервиса импорта клиентов (и сделок) для брокера из админки.
    """

    def __init__(
        self,
        user_repo: Type[UserRepo],
        import_clients_service: ImportClientsService,
        import_clients_all_booking_service: ImportClientsAllBookingService,
    ):
        self.user_repo: UserRepo = user_repo()
        self.import_clients_service = import_clients_service
        self.import_clients_all_booking_service = import_clients_all_booking_service

        self.logger = structlog.getLogger(__name__)

    async def __call__(
        self,
        payload: RequestImportClientsAndBookingsModel,
    ) -> None:

        broker: User = await self.user_repo.retrieve(filters=dict(id=payload.broker_id))

        if broker.is_deleted:
            self.logger.warning(
                f"Брокер {broker} удален из кабинета"
            )
            raise UserWasDeletedError

        if self.__is_strana_lk_3412_enable():
            self.logger.debug(f"3412 payload.broker_id={payload.broker_id}")

            # TOD
            create_task(self.import_clients_all_booking_service(agent_id=payload.broker_id))
            # await self.import_clients_all_booking_service(agent_id=payload.broker_id)
        else:
            create_task(self.import_clients_service(agent_id=payload.broker_id))

    def __is_strana_lk_3412_enable(self) -> bool:
        return UnleashClient().is_enabled(FeatureFlags.strana_lk_3412)
