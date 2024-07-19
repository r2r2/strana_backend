import logging

from structlog.typing import FilteringBoundLogger

from sdk.db.session import AsyncSession
from .dao import LocalDAO


class ClearImportDataService:
    def __init__(
        self,
        session: AsyncSession,
        logger: FilteringBoundLogger,
    ) -> None:
        self._dao = LocalDAO(session)
        self._logger = logger
        logging.basicConfig()

    async def run(self) -> None:
        await self._dao.clear_import_logs()
        await self._dao.clear_load_event_games()
