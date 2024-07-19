from datetime import datetime

from portal_liga_pro_db import Tournaments
from sqlalchemy import select

from sdk.db.dao.base import BaseDAO


class LocalDAO(BaseDAO):
    async def get_tournaments_by_sport(
        self, *, sport_ids: list[int], from_start_at: datetime, to_start_at: datetime
    ) -> list[int]:
        query = (
            select(Tournaments.id)
            .where(
                Tournaments.start_at >= from_start_at,
                Tournaments.start_at < to_start_at,
                Tournaments.sport_id.in_(sport_ids),
            )
            .order_by(Tournaments.start_at)
        )
        return await self._get_scalars(query)
