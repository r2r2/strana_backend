from portal_liga_pro_db import Games, ImportLogs
from sqlalchemy import delete, update

from sdk.db.dao.base import BaseDAO


class LocalDAO(BaseDAO):
    async def clear_import_logs(self) -> None:
        query = delete(ImportLogs)
        await self._execute(query)

    async def clear_load_event_games(self) -> None:
        query = update(Games).where(Games.is_load_events.is_(True)).values(is_load_events=False)
        await self._execute(query)
