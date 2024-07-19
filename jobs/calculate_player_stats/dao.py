from collections.abc import Iterable

from portal_liga_pro_db import Games, GameStateEnum, Players, Sides, Teams
from sqlalchemy import func, or_, select
from sqlalchemy.engine import Row

from sdk.db.dao.base import BaseDAO


class LocalDAO(BaseDAO):
    async def get_player_ids(self, sport_id: int) -> list[int]:
        query = (
            select(Players.id)
            .select_from(Players)
            .join(Sides, Players.id == Sides.player_id)
            .where(Players.sport_id == sport_id)
        )
        return await self._get_scalars(query)

    async def get_games_by_sport_ids(self, sport_ids: Iterable[int]) -> Iterable[Row]:
        subquery = (
            select(
                Players.id.label("player_id"),
                Players.sport_id,
                Games.id.label("game_id"),
                Games.start_game,
                func.rank().over(partition_by=Players.id, order_by=Games.start_game.desc()).label("game_rank"),
            )
            .join(Sides, Sides.player_id == Players.id)
            .join(Games, or_(Games.side_one_id == Sides.id, Games.side_two_id == Sides.id))
            .where(Players.sport_id.in_(sport_ids))
            .where(Games.state == GameStateEnum.FINISHED)
            .subquery()
        )

        query = (
            select(subquery.c.player_id, subquery.c.sport_id, subquery.c.game_id, subquery.c.start_game)
            .select_from(subquery)
            .where(subquery.c.game_rank == 1)
        )

        return await self._fetch_all(query)

    async def get_team_ids(self, sport_id: int) -> list[int]:
        query = (
            select(Teams.id)
            .select_from(Teams)
            .join(Sides, Teams.id == Sides.player_id)
            .where(Teams.sport_id == sport_id)
        )
        return await self._get_scalars(query)
