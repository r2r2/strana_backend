from collections.abc import Iterable
from datetime import time
from typing import Any

from portal_liga_pro_db import (
    GameResults,
    Games,
    GameSides,
    GameStateEnum,
    ImportLogs,
    PlayerRatings,
    Players,
    Sides,
    SportEnum,
    Stages,
    Teams,
    Tournaments,
    TournamentSides,
    TournamentStageSides,
    TournamentStateEnum,
    TournamentTimes,
)
from sqlalchemy import insert, select, update
from sqlalchemy.engine import Row

from jobs.import_lp_dump.models import Places
from jobs.import_lp_dump.schemas import (
    Game,
    Player,
    Side,
    Team,
    TournamentSide,
    TournamentStageSide,
    TournamentState,
)
from sdk.db.dao.base import BaseDAO


class LocalDAO(BaseDAO):
    async def _get_or_create_player(self, player: Player, *, sport_id: int) -> int:
        expression = Players.sl_id == player.sl_id if player.sl_id else Players.old_id == player.old_lp_id
        query = select(Players.id).select_from(Players).where(expression)
        player_id = await self._get_scalar_or_none(query)
        if not player_id:
            query = (
                insert(Players)
                .values(
                    sport_id=sport_id,
                    old_id=player.old_lp_id,
                    fntr_id=player.fntr_id,
                    sl_id=player.sl_id,
                    first_name_ru=player.first_name_ru,
                    first_name_en=player.first_name_en,
                    surname_ru=player.surname_ru,
                    surname_en=player.surname_en,
                    patronymic_ru=player.patronymic_ru,
                    patronymic_en=player.patronymic_en,
                    short_name_ru=player.short_name_ru,
                    short_name_en=player.short_name_en,
                    nickname=player.nickname,
                    search_field=player.search_field,
                    email=player.email,
                    phone=player.phone,
                    birthday=player.birthday,
                    gender_id=player.gender_id,
                    rating=player.rating,
                    rating_date=player.rating_date,
                    is_history=True,
                )
                .returning(Players.id)
            )
            player_id = await self._get_scalar_one(query)
        return player_id  # type: ignore

    async def _get_or_create_team(self, team: Team, *, sport_id: int) -> int:
        expression = Teams.sl_id == team.sl_id if team.sl_id else Teams.old_id == team.old_lp_id
        query = select(Teams.id).select_from(Teams).where(expression)
        team_id = await self._get_scalar_or_none(query)
        if not team_id:
            query = (
                insert(Teams)
                .values(
                    sport_id=sport_id,
                    old_id=team.old_lp_id,
                    sl_id=team.sl_id,
                    team_captain_id=team.team_captain_id,
                    name_ru=team.name_ru,
                    name_en=team.name_en,
                    short_name_ru=team.short_name_ru,
                    short_name_en=team.short_name_en,
                    search_field=team.search_field,
                    gender_id=team.gender_id,
                    city_id=team.city_id,
                    phone=team.phone,
                    rating=team.rating,
                    is_history=True,
                )
                .returning(Teams.id)
            )
            team_id = await self._get_scalar_one(query)
        return team_id  # type: ignore

    async def _create_game_results(self, game: Game, *, game_id: int) -> None:
        query = insert(GameResults).values(
            game_id=game_id,
            score_one=game.score_one,
            score_two=game.score_two,
            period_scores=game.period_scores,
            duration=game.duration,
        )
        await self._execute(query)

    async def _create_game_sides(self, side_ids: Iterable[int], *, game_id: int) -> None:
        values = [
            {
                "game_id": game_id,
                "side_id": side_id,
            }
            for side_id in side_ids
        ]
        query = insert(GameSides).values(values)
        await self._execute(query)

    async def get_or_create_old_side(self, side: Side, *, sport_id: int) -> tuple[int, int | None, int | None]:
        team_id = None
        player_id = None
        if side.team:
            team_id = await self._get_or_create_team(side.team, sport_id=sport_id)
        if side.player:
            player_id = await self._get_or_create_player(side.player, sport_id=sport_id)
        query = (
            select(Sides.id, Sides.team_id, Sides.player_id)
            .select_from(Sides)
            .where(Sides.player_id == player_id, Sides.team_id == team_id)
        )
        side_info = await self._fetch_one(query)
        if side_info:
            side_id = side_info.id
            team_id = side_info.team_id
            player_id = side_info.player_id
        else:
            query = (
                insert(Sides)
                .values(
                    sport_id=sport_id,
                    sl_id=side.sl_id,
                    type_id=side.type_id,
                    team_id=team_id,
                    player_id=player_id,
                    is_history=True,
                )
                .returning(Sides.id)
            )
            side_id = await self._get_scalar_one(query)
        return side_id, team_id, player_id

    async def get_or_create_side(self, side: Side, *, sport_id: int) -> tuple[int, int | None, int | None]:
        query = select(Sides.id, Sides.team_id, Sides.player_id).select_from(Sides).where(Sides.sl_id == side.sl_id)
        side_info = await self._fetch_one(query)
        if side_info:
            side_id = side_info.id
            team_id = side_info.team_id
            player_id = side_info.player_id
        else:
            team_id = None
            player_id = None
            if side.team:
                team_id = await self._get_or_create_team(side.team, sport_id=sport_id)
            if side.player:
                player_id = await self._get_or_create_player(side.player, sport_id=sport_id)
            query = (
                insert(Sides)
                .values(
                    sport_id=sport_id,
                    sl_id=side.sl_id,
                    type_id=side.type_id,
                    team_id=team_id,
                    player_id=player_id,
                    is_history=True,
                )
                .returning(Sides.id)
            )
            side_id = await self._get_scalar_one(query)
        return side_id, team_id, player_id

    async def get_or_create_tournament_times(self, time_start: time, *, sport_id: int) -> int:
        query = (
            select(TournamentTimes.id)
            .select_from(TournamentTimes)
            .where(TournamentTimes.time == time_start, TournamentTimes.sport_id == sport_id)
        )
        tournament_time_id = await self._get_scalar_or_none(query)
        if not tournament_time_id:
            query = (
                insert(TournamentTimes)
                .values(
                    sport_id=sport_id,
                    time=time_start,
                )
                .returning(TournamentTimes.id)
            )
            tournament_time_id = await self._get_scalar_one(query)
        return tournament_time_id  # type: ignore

    async def get_place(self, old_lp_id: int, *, sport_id: int) -> int | None:
        query = select(Places.id).select_from(Places).where(Places.old_id == old_lp_id, Places.sport_id == sport_id)
        return await self._get_scalar_or_none(query)

    async def get_stages_map(self, stage_old_lp_ids: Iterable[int], *, sport_id: int) -> dict[int, int]:
        query = (
            select(Stages.id, Stages.old_id)
            .select_from(Stages)
            .where(Stages.old_id.in_(stage_old_lp_ids), Stages.sport_id == sport_id)
        )
        rows = await self._fetch_all(query)
        return {row.old_id: row.id for row in rows}

    async def create_tournament(
        self,
        tournament: TournamentState,
        *,
        tournament_time_id: int,
        place_id: int | None,
    ) -> int:
        query = (
            insert(Tournaments)
            .values(
                old_id=tournament.old_lp_id,
                sport_id=tournament.sport_id,
                place_id=place_id,
                organizer_id=1,
                category_id=tournament.category_id,
                gender_id=tournament.gender_id,
                side_type_id=tournament.side_type_id,
                start_at=tournament.start_at,
                time_start_id=tournament_time_id,
                end_date_at=tournament.end_date_at,
                name_ru=tournament.name_ru,
                name_en=tournament.name_en,
                address=tournament.address,
                text_ru=tournament.text_ru,
                text_en=tournament.text_en,
                youtube=tournament.youtube,
                state=TournamentStateEnum.FINISHED,
                sides_count=len(tournament.sides),
                matches_count=len(tournament.games),
                is_history=True,
            )
            .returning(Tournaments.id)
        )
        return await self._get_scalar_one(query)  # type: ignore

    async def create_tournament_sides(
        self,
        tournament_sides: list[TournamentSide],
        *,
        tournament_id: int,
        sport_id: int,
        sides_map: dict[int, int],
    ) -> None:
        values = [
            {
                "tournament_id": tournament_id,
                "side_id": sides_map[tournament_side.old_side_id],
                "sport_id": sport_id,
                "place": tournament_side.place,
                "auto_place": tournament_side.auto_place,
                "rating_before": tournament_side.rating_before,
                "rating_after": tournament_side.rating_after,
                "delta": tournament_side.delta,
                "date_reg": tournament_side.date_reg,
            }
            for tournament_side in tournament_sides
        ]
        query = insert(TournamentSides).values(values)
        await self._execute(query)

    async def create_tournament_stage_sides(
        self,
        tournament_stage_sides: list[TournamentStageSide],
        *,
        tournament_id: int,
        sport_id: int,
        sides_map: dict[int, int],
    ) -> None:
        values = [
            {
                "tournament_id": tournament_id,
                "side_id": sides_map[tournament_stage_side.old_side_id],
                "sport_id": sport_id,
                "tour_number": tournament_stage_side.tour_number,
                "place": tournament_stage_side.place,
            }
            for tournament_stage_side in tournament_stage_sides
        ]
        query = insert(TournamentStageSides).values(values)
        await self._execute(query)

    async def create_game(
        self,
        game: Game,
        *,
        tournament_id: int,
        sport_id: int,
        sides_map: dict[int, int],
        stages_map: dict[int, int],
    ) -> None:
        query = (
            insert(Games)
            .values(
                old_id=game.old_lp_id,
                sl_id=game.sl_id,
                sport_id=sport_id,
                tournament_id=tournament_id,
                stage_id=stages_map[game.stage_old_lp_id],
                state=GameStateEnum.FINISHED,
                start_game=game.start_game,
                side_one_id=sides_map[game.old_side_one_id],
                side_two_id=sides_map[game.old_side_two_id],
                youtube=game.youtube,
                is_doubles=0,
            )
            .returning(Games.id)
        )
        game_id = await self._get_scalar_one(query)
        await self._create_game_results(game, game_id=game_id)
        side_ids = (sides_map[game.old_side_one_id], sides_map[game.old_side_two_id])
        await self._create_game_sides(side_ids, game_id=game_id)

    async def log_error(self, tournament_id: int, message: str) -> None:
        query = insert(ImportLogs).values(lp_dump_tournament_id=tournament_id, message=message)
        await self._execute(query)

    async def add_player_ratings(self, insert_data: list[dict[str, Any]]) -> None:
        query = insert(PlayerRatings).values(insert_data)
        await self._execute(query)

    async def get_players_map(self, sport_id: SportEnum) -> tuple[dict[int, int], dict[int, int]]:
        query = (
            select(
                Players.id,
                Players.sl_id,
                Players.old_id,
            )
            .select_from(Players)
            .join(Sides, Sides.player_id == Players.id)
            .where(Players.sport_id == sport_id, Players.deleted_at.is_(None))
        )
        rows = await self._fetch_all(query)
        sl_ids_map = {}
        old_ids_map = {}
        for row in rows:
            sl_ids_map[row.sl_id] = row.id
            old_ids_map[row.old_id] = row.id
        return sl_ids_map, old_ids_map

    async def get_sides_map(self, sport: SportEnum) -> dict[int, int]:
        query = (
            select(Sides.id, Sides.sl_id)
            .select_from(Sides)
            .where(Sides.team_id == 211, Sides.sport_id == sport)
            .order_by(Sides.sl_id)
        )
        rows = await self._fetch_all(query)
        return {row.sl_id: row.id for row in rows}

    async def create_team(self, team: Row, sport: SportEnum) -> int:
        query = select(Teams.id).select_from(Teams).where(Teams.old_id == team.old_id, Teams.sport_id == sport)
        team_id = await self._get_scalar_or_none(query)
        if team_id:
            query = update(Teams).where(Teams.id == team_id).values(sl_id=team.sl_id)
            await self._execute(query)
        else:
            query = (
                insert(Teams)
                .values(
                    sport_id=sport,
                    old_id=team.old_id,
                    sl_id=team.sl_id,
                    name_ru=team.name_ru,
                    name_en=team.name_en,
                    short_name_ru=team.short_name_ru,
                    short_name_en=team.short_name_en,
                    team_captain_id=team.team_captain_id,
                    search_field=team.search_field,
                    gender_id=team.gender_id,
                    city_id=team.city_id,
                    phone=team.phone,
                    rating=team.rating,
                    is_history=True,
                )
                .returning(Teams.id)
            )
            team_id = await self._get_scalar_one(query)
        return team_id  # type: ignore

    async def create_player(self, player: Row, sport: SportEnum) -> int:
        query = (
            select(Players.id).select_from(Players).where(Players.old_id == player.old_id, Players.sport_id == sport)
        )
        player_id = await self._get_scalar_or_none(query)
        if player_id:
            query = update(Players).where(Players.id == player_id).values(sl_id=player.sl_id)
            await self._execute(query)
        else:
            query = (
                insert(Players)
                .values(
                    sport_id=sport,
                    old_id=player.old_id,
                    fntr_id=player.fntr_id,
                    sl_id=player.sl_id,
                    first_name_ru=player.first_name_ru,
                    first_name_en=player.first_name_en,
                    surname_ru=player.surname_ru,
                    surname_en=player.surname_en,
                    patronymic_ru=player.patronymic_ru,
                    patronymic_en=player.patronymic_en,
                    short_name_ru=player.short_name_ru,
                    short_name_en=player.short_name_en,
                    nickname=player.nickname,
                    search_field=player.search_field,
                    email=player.email,
                    phone=player.phone,
                    birthday=player.birthday,
                    gender_id=player.gender_id,
                    rating=player.rating,
                    rating_date=player.rating_date,
                    is_history=True,
                )
                .returning(Players.id)
            )
            player_id = await self._get_scalar_one(query)
        return player_id  # type: ignore

    async def update_side_players(self, side_id: int, *, values: dict[str, Any]) -> None:
        query = update(Sides).where(Sides.id == side_id).values(**values)
        await self._execute(query)
