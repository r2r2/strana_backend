from collections.abc import Iterable
from datetime import datetime

from portal_liga_pro_db import SportEnum
from sqlalchemy import func, select
from sqlalchemy.engine import Row

from jobs.import_lp_dump.models import (
    GameResults,
    Games,
    Places,
    PlayerRatings,
    Players,
    Sides,
    Stages,
    Teams,
    Tournaments,
    TournamentSides,
    TournamentStageSides,
)
from sdk.db.dao.base import BaseDAO


class OldLpDAO(BaseDAO):
    async def get_tournaments_total_count(self, sport_id: int, *, start_at: datetime, end_at: datetime) -> int:
        query = (
            select(func.count())
            .select_from(Tournaments)
            .where(
                Tournaments.sport_id == sport_id,
                Tournaments.start_at >= start_at,
                Tournaments.start_at < end_at,
                Tournaments.category_id.is_not(None),
            )
        )
        return await self._get_scalar_one(query)  # type: ignore

    async def get_player_ratings(
        self,
        sport_id: SportEnum,
        *,
        limit: int,
        offset: int,
    ) -> list[Row]:
        query = (
            select(
                PlayerRatings.player_id,
                Players.old_id.label("player_old_id"),
                Players.sl_id.label("player_sl_id"),
                PlayerRatings.rating,
                PlayerRatings.date_at,
            )
            .select_from(PlayerRatings)
            .join(Players, PlayerRatings.player_id == Players.id)
            .where(Players.sport_id == sport_id, PlayerRatings.date_at.is_not(None))
            .order_by(PlayerRatings.id)
            .limit(limit)
            .offset(offset)
        )
        return await self._fetch_all(query)

    async def get_tournaments(
        self,
        sport_id: int,
        *,
        start_at: datetime,
        end_at: datetime,
        limit: int,
        offset: int,
    ) -> list[Row]:
        query = (
            select(
                Tournaments.id.label("old_id"),
                Tournaments.old_id.label("old_lp_id"),
                Tournaments.sl_id,
                Tournaments.sport_id,
                Places.old_id.label("place_old_lp_id"),
                Tournaments.category_id,
                Tournaments.gender_id,
                Tournaments.side_type_id,
                Tournaments.start_at,
                Tournaments.end_date_at,
                Tournaments.name_ru,
                Tournaments.name_en,
                Tournaments.address,
                Tournaments.text_ru,
                Tournaments.text_en,
                Tournaments.youtube,
            )
            .select_from(Tournaments)
            .join(Places, Tournaments.place_id == Places.id, isouter=True)
            .where(
                Tournaments.sport_id == sport_id,
                Tournaments.start_at >= start_at,
                Tournaments.start_at < end_at,
                Tournaments.category_id.is_not(None),
            )
            .order_by(Tournaments.id)
            .limit(limit)
            .offset(offset)
        )
        return await self._fetch_all(query)

    async def get_tournament_sides_map(self, tournament_ids: Iterable[int]) -> dict[int, list[Row]]:
        query = (
            select(
                TournamentSides.id.label("old_id"),
                TournamentSides.tournament_id.label("old_tournament_id"),
                TournamentSides.side_id.label("old_side_id"),
                TournamentSides.place,
                TournamentSides.auto_place,
                TournamentSides.rating_before,
                TournamentSides.rating_after,
                TournamentSides.delta,
                TournamentSides.date_reg,
            )
            .select_from(TournamentSides)
            .where(TournamentSides.tournament_id.in_(tournament_ids))
            .order_by(TournamentSides.tournament_id)
        )
        rows = await self._fetch_all(query)
        tournament_sides_map: dict[int, list[Row]] = {}
        for row in rows:
            tournament_sides_map.setdefault(row.old_tournament_id, []).append(row)
        return tournament_sides_map

    async def get_tournament_stage_sides_map(self, tournament_ids: Iterable[int]) -> dict[int, list[Row]]:
        query = (
            select(
                TournamentStageSides.id.label("old_id"),
                TournamentStageSides.tournament_id.label("old_tournament_id"),
                TournamentStageSides.side_id.label("old_side_id"),
                TournamentStageSides.tour_number,
                TournamentStageSides.place,
            )
            .select_from(TournamentStageSides)
            .where(TournamentStageSides.tournament_id.in_(tournament_ids))
            .order_by(TournamentStageSides.tournament_id)
        )
        rows = await self._fetch_all(query)
        tournament_stage_sides_map: dict[int, list[Row]] = {}
        for row in rows:
            tournament_stage_sides_map.setdefault(row.old_tournament_id, []).append(row)
        return tournament_stage_sides_map

    async def get_games_map(self, tournament_ids: Iterable[int]) -> dict[int, list[Row]]:
        query = (
            select(
                Games.id.label("old_id"),
                Games.old_id.label("old_lp_id"),
                Games.sl_id,
                Games.tournament_id.label("old_tournament_id"),
                Stages.old_id.label("stage_old_lp_id"),
                Games.start_game,
                Games.side_one_id.label("old_side_one_id"),
                Games.side_two_id.label("old_side_two_id"),
                Games.youtube,
                GameResults.score_one,
                GameResults.score_two,
                GameResults.period_scores,
                GameResults.duration,
            )
            .select_from(Games)
            .join(GameResults, Games.id == GameResults.game_id)
            .join(Stages, Games.stage_id == Stages.id)
            .where(Games.tournament_id.in_(tournament_ids))
            .order_by(Games.tournament_id)
        )
        rows = await self._fetch_all(query)
        games_map: dict[int, list[Row]] = {}
        for row in rows:
            games_map.setdefault(row.old_tournament_id, []).append(row)
        return games_map

    async def get_sides_map(self, side_ids: Iterable[int]) -> dict[int, Row]:
        query = (
            select(
                Sides.id.label("old_id"),
                Sides.sl_id,
                Sides.type_id,
                Teams.id.label("team_old_id"),
                Teams.old_id.label("team_old_lp_id"),
                Teams.sl_id.label("team_sl_id"),
                Teams.team_captain_id.label("team_team_captain_id"),
                Teams.name_ru.label("team_name_ru"),
                Teams.name_en.label("team_name_en"),
                Teams.short_name_ru.label("team_short_name_ru"),
                Teams.short_name_en.label("team_short_name_en"),
                Teams.search_field.label("team_search_field"),
                Teams.gender_id.label("team_gender_id"),
                Teams.city_id.label("team_city_id"),
                Teams.phone.label("team_phone"),
                Teams.rating.label("team_rating"),
                Players.id.label("player_old_id"),
                Players.old_id.label("player_old_lp_id"),
                Players.sl_id.label("player_sl_id"),
                Players.fntr_id.label("player_fntr_id"),
                Players.first_name_ru.label("player_first_name_ru"),
                Players.first_name_en.label("player_first_name_en"),
                Players.surname_ru.label("player_surname_ru"),
                Players.surname_en.label("player_surname_en"),
                Players.patronymic_ru.label("player_patronymic_ru"),
                Players.patronymic_en.label("player_patronymic_en"),
                Players.short_name_ru.label("player_short_name_ru"),
                Players.short_name_en.label("player_short_name_en"),
                Players.nickname.label("player_nickname"),
                Players.search_field.label("player_search_field"),
                Players.email.label("player_email"),
                Players.phone.label("player_phone"),
                Players.birthday.label("player_birthday"),
                Players.gender_id.label("player_gender_id"),
                Players.rating.label("player_rating"),
                Players.rating_date.label("player_rating_date"),
            )
            .select_from(Sides)
            .join(Players, Sides.player_id == Players.id, isouter=True)
            .join(Teams, Sides.team_id == Teams.id, isouter=True)
            .where(Sides.id.in_(side_ids))
        )
        rows = await self._fetch_all(query)
        return {row.old_id: row for row in rows}

    async def get_players_by_sl_id(self, side_sl_ids: Iterable[int]) -> list[Row]:
        query = (
            select(
                Players.id,
                Players.old_id,
                Players.sl_id,
                Players.fntr_id,
                Players.first_name_ru,
                Players.first_name_en,
                Players.surname_ru,
                Players.surname_en,
                Players.patronymic_ru,
                Players.patronymic_en,
                Players.short_name_ru,
                Players.short_name_en,
                Players.nickname,
                Players.search_field,
                Players.email,
                Players.phone,
                Players.birthday,
                Players.gender_id,
                Players.rating,
                Players.rating_date,
            )
            .select_from(Players)
            .where(Players.sl_id.in_(side_sl_ids))
        )
        return await self._fetch_all(query)

    async def get_teams_by_sl_id(self, side_sl_ids: Iterable[int]) -> list[Row]:
        query = (
            select(
                Teams.id,
                Teams.old_id,
                Teams.sl_id,
                Teams.team_captain_id,
                Teams.name_ru,
                Teams.name_en,
                Teams.short_name_ru,
                Teams.short_name_en,
                Teams.search_field,
                Teams.gender_id,
                Teams.city_id,
                Teams.phone,
                Teams.rating,
            )
            .select_from(Teams)
            .where(Teams.sl_id.in_(side_sl_ids))
        )
        return await self._fetch_all(query)
