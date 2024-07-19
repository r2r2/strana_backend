import logging
import traceback
from collections.abc import AsyncGenerator, Awaitable, Callable
from typing import Any

from portal_liga_pro_db import SideTypesEnum, SportEnum
from redis.asyncio import Redis
from sqlalchemy.engine import Row
from structlog.typing import FilteringBoundLogger

from jobs.internal.app_settings import ImportLPDumpSettings, ImportLPDumpTypeEnum
from sdk.db.session import AsyncSession
from .dao.local import LocalDAO
from .dao.old_lp import OldLpDAO
from .schemas import Player, Side, Team, TournamentState


class ImportLPDumpService:
    def __init__(
        self,
        job_settings: ImportLPDumpSettings,
        session: AsyncSession,
        lp_dump_session: AsyncSession,
        redis: "Redis[Any]",
        logger: FilteringBoundLogger,
    ):
        self._job_settings = job_settings
        self._local_session = session
        self._local_dao = LocalDAO(session)
        self._old_lp_dao = OldLpDAO(lp_dump_session)
        self._logger = logger
        self._redis = redis
        logging.basicConfig()

    async def _old_lp_tournaments_paginator(self, total_count: int) -> AsyncGenerator[TournamentState, None]:
        for offset in range(0, total_count, self._job_settings.load_tournaments_count):
            tournaments = await self._old_lp_dao.get_tournaments(
                self._job_settings.sport_id,
                start_at=self._job_settings.tournament_start_at,
                end_at=self._job_settings.tournament_end_at,
                limit=self._job_settings.load_tournaments_count,
                offset=offset,
            )
            tournament_ids = []
            for tournament in tournaments:
                tournament_ids.append(tournament.old_id)
            tournament_sides_map = await self._old_lp_dao.get_tournament_sides_map(tournament_ids)
            tournament_stage_sides_map = await self._old_lp_dao.get_tournament_stage_sides_map(tournament_ids)
            games_map = await self._old_lp_dao.get_games_map(tournament_ids)
            side_ids = [
                tournament_side.old_side_id
                for tournament_sides in tournament_sides_map.values()
                for tournament_side in tournament_sides
            ]
            sides_map = await self._old_lp_dao.get_sides_map(side_ids)

            for tournament in tournaments:
                sides = [
                    Side(
                        **sides_map[tournament_side.old_side_id],
                        team=Team.create_with_scope(sides_map[tournament_side.old_side_id], scope="team"),
                        player=Player.create_with_scope(sides_map[tournament_side.old_side_id], scope="player"),
                    )
                    for tournament_side in tournament_sides_map[tournament.old_id]
                ]
                yield TournamentState(
                    **tournament,
                    sides=sides,
                    tournament_sides=tournament_sides_map[tournament.old_id],
                    tournament_stage_sides=tournament_stage_sides_map.get(tournament.old_id, []),
                    games=games_map[tournament.old_id],
                )

    async def _save_tournament(self, tournament: TournamentState) -> None:
        players_map = {}
        teams_map = {}
        sides_map = {}
        for side in tournament.sides:
            if side.sl_id:
                side_id, team_id, player_id = await self._local_dao.get_or_create_side(
                    side,
                    sport_id=tournament.sport_id,
                )
            else:
                side_id, team_id, player_id = await self._local_dao.get_or_create_old_side(
                    side,
                    sport_id=tournament.sport_id,
                )
            if side.player and player_id:
                players_map[side.player.old_id] = player_id
            if side.team and team_id:
                teams_map[side.team.old_id] = team_id
            sides_map[side.old_id] = side_id
        tournament_time_id = await self._local_dao.get_or_create_tournament_times(
            tournament.time_start,
            sport_id=tournament.sport_id,
        )
        place_id = None
        if tournament.place_old_lp_id:
            place_id = await self._local_dao.get_place(tournament.place_old_lp_id, sport_id=tournament.sport_id)
        stage_old_lp_ids = {game.stage_old_lp_id for game in tournament.games}
        stages_map = await self._local_dao.get_stages_map(stage_old_lp_ids, sport_id=tournament.sport_id)
        tournament_id = await self._local_dao.create_tournament(
            tournament,
            tournament_time_id=tournament_time_id,
            place_id=place_id,
        )
        await self._local_dao.create_tournament_sides(
            tournament.tournament_sides,
            tournament_id=tournament_id,
            sport_id=tournament.sport_id,
            sides_map=sides_map,
        )
        if tournament.tournament_stage_sides:
            await self._local_dao.create_tournament_stage_sides(
                tournament.tournament_stage_sides,
                tournament_id=tournament_id,
                sport_id=tournament.sport_id,
                sides_map=sides_map,
            )
        for game in tournament.games:
            await self._local_dao.create_game(
                game,
                tournament_id=tournament_id,
                sport_id=tournament.sport_id,
                sides_map=sides_map,
                stages_map=stages_map,
            )

    async def _import_lp_dump(self) -> None:
        total_count = await self._old_lp_dao.get_tournaments_total_count(
            self._job_settings.sport_id,
            start_at=self._job_settings.tournament_start_at,
            end_at=self._job_settings.tournament_end_at,
        )
        async for tournament in self._old_lp_tournaments_paginator(total_count):
            try:
                await self._save_tournament(tournament)
            except Exception:  # noqa: PIE786
                await self._local_session.rollback()
                await self._local_dao.log_error(tournament.old_id, traceback.format_exc())
                await self._local_session.commit()
            else:
                await self._local_session.commit()

    async def _import_rating(self) -> None:
        limit = 1000
        offset = 0
        sl_players_map, old_players_map = await self._local_dao.get_players_map(self._job_settings.sport_id)
        while True:
            player_ratings = await self._old_lp_dao.get_player_ratings(
                self._job_settings.sport_id, limit=limit, offset=offset
            )
            if not player_ratings:
                break
            insert_data = []
            for player_rating in player_ratings:
                player_sl_id = player_rating.player_sl_id
                player_old_id = player_rating.player_old_id
                player_id = sl_players_map.get(player_sl_id) or old_players_map.get(player_old_id)
                if player_id:
                    insert_data.append(
                        {
                            "player_id": player_id,
                            "rating": player_rating.rating,
                            "date_at": player_rating.date_at,
                        }
                    )
            await self._local_dao.add_player_ratings(insert_data)
            await self._local_session.commit()
            offset += limit

    async def _fix_participants(self) -> None:
        sport = SportEnum(self._job_settings.sport_id)
        sides_map = await self._local_dao.get_sides_map(sport)
        create_participant: Callable[[Row, SportEnum], Awaitable[int]]
        if sport.side_type == SideTypesEnum.TEAMS:
            participants = await self._old_lp_dao.get_teams_by_sl_id(sides_map.keys())
            create_participant = self._local_dao.create_team
            field = "team_id"
        elif sport.side_type == SideTypesEnum.PLAYERS:
            participants = await self._old_lp_dao.get_players_by_sl_id(sides_map.keys())
            create_participant = self._local_dao.create_player
            field = "player_id"
        else:
            raise Exception()
        for participant in participants:
            participant_id = await create_participant(participant, sport)
            await self._local_dao.update_side_players(sides_map[participant.sl_id], values={field: participant_id})
        await self._local_session.commit()

    async def run(self) -> None:
        if self._job_settings.import_type == ImportLPDumpTypeEnum.ALL:
            await self._import_lp_dump()
        elif self._job_settings.import_type == ImportLPDumpTypeEnum.RATING:
            await self._import_rating()
        else:
            await self._fix_participants()
