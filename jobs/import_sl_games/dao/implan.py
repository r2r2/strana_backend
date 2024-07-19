from collections import defaultdict
from collections.abc import Iterable
from datetime import datetime

from sqlalchemy import case, column, select
from sqlalchemy.engine import Row
from sqlalchemy.orm import aliased

from sdk.db.dao.base import BaseDAO
from sdk.db.models.sl_implan import (
    Event,
    Leagues,
    Meet,
    MeetTranslation,
    Round,
    RoundTeam,
    StageType,
    Team,
    Translation,
)


class ImplanDAO(BaseDAO):
    async def get_event_rounds(
        self,
        event_id: int,
        created_date_from: datetime | None,
        *,
        ignore_sl_ids: list[int],
        limit: int,
        offset: int,
    ) -> list[Row]:
        from_start_at = created_date_from or datetime.utcnow()
        query = (
            select(
                Round.id,
                Round.title_ru,
                Round.title_en,
                Round.start_at,
                Round.finish_at,
                Leagues.id.label("league_id"),
                Leagues.title_ru.label("league_title_ru"),
                Leagues.title_en.label("league_title_en"),
                Event.id.label("event_id"),
                Event.title_ru.label("event_title_ru"),
                Event.title_en.label("event_title_en"),
                Event.gender_id,
            )
            .select_from(Round)
            .where(Round.event_id == event_id, Round.start_at > from_start_at, Round.id.not_in(ignore_sl_ids))
            .join(Event, Round.event_id == Event.id)
            .join(Leagues, Round.league_id == Leagues.id, isouter=True)
            .order_by(Round.id)
            .limit(limit)
            .offset(offset)
        )
        return await self._fetch_all(query)

    async def get_round_games(
        self,
        round_ids: Iterable[int],
    ) -> dict[int, list[Row]]:
        query = (
            select(
                Translation.id,
                column("round_id"),
                Translation.team_a_id,
                Translation.team_b_id,
                MeetTranslation.meet_id,
                Translation.stage_type_id,
                Translation.start_at,
                Translation.finish_at,
                Translation.state_id,
            )
            .select_from(Translation)
            .join(MeetTranslation, Translation.id == MeetTranslation.translation_id, isouter=True)
            .where(column("round_id").in_(round_ids))
            .order_by(Translation.id)
        )
        rows = await self._fetch_all(query)
        round_games_map: dict[int, list[Row]] = {}
        for game in rows:
            round_games_map.setdefault(game.round_id, []).append(game)
        return round_games_map

    async def get_meets_map(self, round_ids: Iterable[int]) -> dict[int, list[Row]]:
        query = (
            select(Meet.id, Meet.round_id, Meet.team_a_id, Meet.team_b_id, Meet.start_at)
            .select_from(Meet)
            .where(Meet.round_id.in_(round_ids))
            .order_by(Meet.round_id, Meet.id)
        )
        rows = await self._fetch_all(query)
        meets_map: dict[int, list[Row]] = {}
        for meet in rows:
            meets_map.setdefault(meet.round_id, []).append(meet)
        return meets_map

    async def get_teams(self, team_ids: Iterable[int]) -> dict[int, Row]:
        query = (
            select(
                Team.id,
                Team.title_ru,
                Team.title_en,
                Team.type_id,
                Team.gender_id,
            )
            .select_from(Team)
            .where(Team.id.in_(team_ids))
        )
        rows = await self._fetch_all(query)
        return {row.id: row for row in rows}

    async def get_stages(self, stage_ids: Iterable[int]) -> dict[int, Row]:
        query = (
            select(
                StageType.id,
                StageType.title_ru,
                StageType.title_en,
            )
            .select_from(StageType)
            .where(StageType.id.in_(stage_ids))
        )
        rows = await self._fetch_all(query)
        return {row.id: row for row in rows}

    async def get_last_updated_games(self, event_ids: Iterable[int], *, last_updated_at: datetime) -> list[Row]:
        team_a_table = aliased(Team)
        team_b_table = aliased(Team)
        query = (
            select(
                Translation.id,
                Translation.event_id,
                team_a_table.id.label("team_a_id"),
                team_a_table.type_id.label("team_a_type_id"),
                team_a_table.title_ru.label("team_a_title_ru"),
                team_a_table.title_en.label("team_a_title_en"),
                team_a_table.gender_id.label("team_a_gender_id"),
                team_b_table.id.label("team_b_id"),
                team_b_table.type_id.label("team_b_type_id"),
                team_b_table.title_ru.label("team_b_title_ru"),
                team_b_table.title_en.label("team_b_title_en"),
                team_b_table.gender_id.label("team_b_gender_id"),
                StageType.id.label("stage_type_id"),
                StageType.title_ru.label("stage_type_title_ru"),
                StageType.title_en.label("stage_type_title_en"),
                Translation.start_at,
                case(
                    (Translation.state_id < 6, 1),
                    else_=4,
                ).label("state"),
            )
            .select_from(Translation)
            .join(team_a_table, Translation.team_a_id == team_a_table.id)
            .join(team_b_table, Translation.team_b_id == team_b_table.id)
            .join(StageType, Translation.stage_type_id == StageType.id)
            .where(
                Translation.event_id.in_(event_ids),
                Translation.updated_at > last_updated_at,
            )
            .order_by(Translation.id)
        )
        return await self._fetch_all(query)

    async def get_last_updated_rounds(self, event_ids: Iterable[int], *, last_updated_at: datetime) -> list[Row]:
        query = (
            select(
                Round.id,
                Round.event_id,
                Round.league_id,
                Round.title_ru,
                Round.title_en,
                Round.start_at,
                Round.finish_at,
                Event.title_ru.label("event_title_ru"),
                Event.title_en.label("event_title_en"),
                Leagues.title_ru.label("league_title_ru"),
                Leagues.title_en.label("league_title_en"),
                Event.gender_id,
            )
            .select_from(Round)
            .join(Event, Round.event_id == Event.id, isouter=True)
            .join(Leagues, Round.league_id == Leagues.id, isouter=True)
            .where(
                Round.event_id.in_(event_ids),
                Round.updated_at > last_updated_at,
            )
            .order_by(Round.id)
        )
        return await self._fetch_all(query)

    async def get_round_teams_map(self, round_ids: Iterable[int]) -> dict[int, dict[int, int]]:
        query = (
            select(RoundTeam.round_id, RoundTeam.team_id, RoundTeam.order)
            .select_from(RoundTeam)
            .where(RoundTeam.round_id.in_(round_ids))
            .order_by(RoundTeam.round_id, RoundTeam.order)
        )
        rows = await self._fetch_all(query)
        round_teams_map: dict[int, dict[int, int]] = defaultdict(dict)
        for row in rows:
            round_teams_map[row.round_id][row.team_id] = row.order
        return round_teams_map
