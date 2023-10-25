import structlog
from typing import Type
from asyncio import create_task

from src.users.entities import BaseUserCase
from src.agents.services import ImportClientsService
from ..models import RequestImportClientsAndBookingsModel
from src.users.repos import User, UserRepo


class ImportClientsAndBookingsModelCase(BaseUserCase):
    """
    Ручной запуск сервиса импорта клиентов (и сделок) для брокера из админки.
    """

    def __init__(
        self,
        user_repo: Type[UserRepo],
        import_clients_service: ImportClientsService,
    ):
        self.user_repo: UserRepo = user_repo()
        self.import_clients_service = import_clients_service

        self.logger = structlog.getLogger(__name__)

    async def __call__(
        self,
        payload: RequestImportClientsAndBookingsModel,
    ) -> None:

        broker: User = await self.user_repo.retrieve(filters=dict(id=payload.broker_id))

        if not broker.auth_first_at:
            self.logger.warning(
                f"Брокер {broker} ни разу не был авторизован в кабинете"
            )

        if not broker.is_deleted:
            self.logger.warning(
                f"Брокер {broker} удален из кабинета"
            )

        create_task(self.import_clients_service(agent_id=payload.broker_id))
