from collections.abc import Iterable
from datetime import datetime
from typing import NamedTuple

from portal_liga_pro_db import Players, Sides, SportEnum
from sqlalchemy import Integer, String, column, select, update, values
from sqlalchemy.engine import Row

from sdk.db.dao.base import BaseDAO
from sdk.db.models.sl_implan import Team

CYBERSPORTS = (SportEnum.E_FOOTBALL, SportEnum.E_HOCKEY, SportEnum.E_BASKETBALL)


class CyberPlayerInfo(NamedTuple):
    id: int
    nickname: str
    short_name_ru: str
    short_name_en: str
    search_field: str


class LocalDAO(BaseDAO):
    async def delete_duplicates(self) -> None:
        select_query = (
            select(Players.id)
            .join(Sides, Sides.player_id == Players.id, isouter=True)
            .where(
                Sides.id.is_(None),
                Players.sport_id.in_(CYBERSPORTS),
                Players.deleted_at.is_(None),
            )
        )

        query = update(Players).values(deleted_at=datetime.now()).where(Players.id == select_query.c.id)
        await self._execute(query, synchronize_session="fetch")

    async def get_sl_ids_for_cybers(self) -> list[Row]:
        query = (
            select(
                Sides.player_id,
                Sides.sl_id,
                Players.nickname,
            )
            .distinct(Sides.player_id)
            .select_from(Sides)
            .join(Players, Players.id == Sides.player_id)
            .where(
                Sides.sport_id.in_(CYBERSPORTS),
                Sides.is_tba.is_(False),
                Players.deleted_at.is_(None),
            )
            .order_by(Sides.player_id, Sides.created_at.desc())
        )

        return await self._fetch_all(query)

    async def update_cyber_player_nicknames(self, updated_data: list[CyberPlayerInfo]) -> None:
        values_expression = values(
            column("id", Integer),
            column("nickname", String),
            column("short_name_ru", String),
            column("short_name_en", String),
            column("search_field", String),
            name="values",
        ).data(updated_data)
        query = (
            update(Players)
            .values(
                nickname=values_expression.c.nickname,
                short_name_ru=values_expression.c.short_name_ru,
                short_name_en=values_expression.c.short_name_en,
                search_field=values_expression.c.search_field,
            )
            .where(Players.id == values_expression.c.id)
        )

        await self._execute(query, synchronize_session=False)


class ImplanDAO(BaseDAO):
    async def get_teams(self, team_ids: Iterable[int]) -> list[Row]:
        query = (
            select(
                Team.id,
                Team.title_ru,
                Team.title_en,
            )
            .select_from(Team)
            .where(Team.id.in_(team_ids))
        )
        return await self._fetch_all(query)
