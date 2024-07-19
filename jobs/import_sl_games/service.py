import itertools
import logging
from collections import defaultdict
from collections.abc import Iterable
from datetime import datetime, timedelta
from typing import Any

from portal_liga_pro_db import SideTypesEnum
from redis.asyncio import Redis
from sqlalchemy.engine import Row
from structlog.typing import FilteringBoundLogger

from jobs.settings import get_config
from sdk.db.enums import SideEnum, SportEnum
from sdk.db.session import AsyncSession
from ..internal.app_settings import SLImportEvent
from .dao.implan import ImplanDAO
from .dao.local import LocalDAO
from .schemas import SL_TBA_TAGS, Game, Meet, Side, Stage, TournamentState
from .utils import (
    get_tournament_state,
    join_basketball_games,
    join_basketball_tournaments,
)


class ImportSLGamesService:
    _LOAD_ROUND_PER_PAGE = 500
    _LAST_UPDATED_REDIS_KEY = "importer_sl:last_updated_at"

    def __init__(
        self,
        created_date_from: datetime | None,
        last_updated_hours: int,
        *,
        is_regular: bool,
        session: AsyncSession,
        sl_session: AsyncSession,
        redis: "Redis[Any]",
        logger: FilteringBoundLogger,
        sport: SportEnum | None = None,
        sl_event_ids: list[int] | None = None,
    ):
        config = get_config()
        self._sport = sport
        self._sl_event_ids = sl_event_ids
        self._is_regular = is_regular
        self._last_updated_hours = last_updated_hours
        self._round_start_at = created_date_from if not self._is_regular else None
        self._local_dao = LocalDAO(session)
        self._implan_dao = ImplanDAO(sl_session)
        self._logger = logger
        self._redis = redis
        self._sport_tournament_images = config.sport_tournament_images
        self._basketball_related_sides = config.basketball_related_sides
        self._sl_events_map = config.sl_events
        logging.basicConfig()

    async def _get_last_updated_at(self) -> datetime:
        if self._is_regular:
            last_updated_at = await self._redis.get(self._LAST_UPDATED_REDIS_KEY)
            if isinstance(last_updated_at, int):
                return datetime.fromtimestamp(last_updated_at)
        return datetime.now() - timedelta(hours=self._last_updated_hours)

    async def _set_last_updated_at(self, value: datetime) -> None:
        await self._redis.set(self._LAST_UPDATED_REDIS_KEY, value.timestamp())

    async def _create_side(self, sl_side_id: int, side_info: Side, *, sport: SportEnum) -> int:
        team_id = None
        player_id = None
        if side_info.sport in (SportEnum.TENNIS, SportEnum.TABLE_TENNIS) or side_info.is_part_of_side:
            side_type = SideTypesEnum.PLAYERS
            player_id = await self._local_dao.get_or_create_player(
                side_info.title_ru,
                side_info.title_en,
                side_info.sl_id,
                side_info.sl_gender_id,
                sport=sport,
            )
        elif side_info.sport in (SportEnum.VOLLEYBALL, SportEnum.BASKETBALL, SportEnum.FOOTBALL, SportEnum.HOCKEY):
            side_type = SideTypesEnum.TEAMS
            team_id = await self._local_dao.get_or_create_team(
                side_info.title_ru,
                side_info.title_en,
                side_info.sl_id,
                side_info.sl_gender_id,
                sport=sport,
            )
        elif side_info.sport in (SportEnum.E_FOOTBALL, SportEnum.E_BASKETBALL, SportEnum.E_HOCKEY):
            side_type = SideTypesEnum.TEAMS_PLAYERS
            player_id = await self._local_dao.get_or_create_cyber_player(
                side_info.nickname,  # type: ignore
                sport=sport,
            )
            team_id = await self._local_dao.get_or_create_cyber_team(
                side_info.team_name_ru,  # type: ignore
                side_info.team_name_en,  # type: ignore
                sport=sport,
            )
        else:
            raise Exception()
        return await self._local_dao.get_or_create_side(
            sl_side_id,
            team_id,
            player_id,
            side_type,
            side_info.is_tba,
            sport=sport,
        )

    async def _create_tournament_sides(self, tournament_id: int, tournament: TournamentState) -> dict[int, int]:
        sl_side_ids = {side.sl_id for side in tournament.sides.values()}
        sl_sides_map = await self._local_dao.get_sl_sides(sl_side_ids, tournament.sport)
        tba_side_ids: set[int] = set()
        side_ordering_map: dict[int, int] = {}
        for sl_side_id, side_info in tournament.sides.items():
            if sl_side_id not in sl_sides_map or tournament.sport in (SportEnum.TABLE_TENNIS, SportEnum.TENNIS):
                sl_sides_map[sl_side_id] = await self._create_side(
                    sl_side_id,
                    side_info,
                    sport=tournament.sport,
                )
            if side_info.is_tba:
                tba_side_ids.add(sl_sides_map[sl_side_id])
            if order_by := tournament.side_ordering_map.get(sl_side_id):
                side_ordering_map[sl_sides_map[sl_side_id]] = order_by
        tournament_side_ids = {sl_sides_map[sl_side_id] for sl_side_id in tournament.sl_side_ids}
        side_ratings_map = await self._local_dao.get_side_ratings(tournament.start_at, tournament_side_ids)
        await self._local_dao.create_tournament_sides(
            tournament_id,
            tournament_side_ids,
            tba_side_ids,
            side_ratings_map,
            side_ordering_map=side_ordering_map,
            sport=tournament.sport,
        )
        if tournament.has_group_stage and tournament.max_tour_number:
            await self._local_dao.create_tournament_stage_sides(
                tournament_id,
                tournament_side_ids - tba_side_ids,
                side_ordering_map=side_ordering_map,
                max_tour_number=tournament.max_tour_number,
                sport=tournament.sport,
            )
        return sl_sides_map

    async def _create_stages(self, tournament: TournamentState) -> dict[int, int]:
        sl_stage_ids = {stage.sl_id for stage in tournament.stages.values()}
        sl_stages_map = await self._local_dao.get_sl_stages(sl_stage_ids, sport=tournament.sport)
        for sl_stage_id, stage_info in tournament.stages.items():
            if sl_stage_id not in sl_stages_map:
                sl_stages_map[sl_stage_id] = await self._local_dao.get_or_create_stage(
                    stage_info, sport=tournament.sport
                )
        return sl_stages_map

    async def _create_meets(
        self,
        tournament_id: int,
        tournament: TournamentState,
        *,
        sl_sides_map: dict[int, int],
    ) -> dict[int, int]:
        insert_data = []
        for sl_meet in tournament.meets:
            side_one_id = sl_sides_map[sl_meet.sl_side_one_id]
            side_two_id = sl_sides_map[sl_meet.sl_side_two_id]
            insert_data.append(
                {
                    "sl_id": sl_meet.sl_id,
                    "sport_id": sl_meet.sport,
                    "tournament_id": tournament_id,
                    "start_at": sl_meet.start_at,
                    "side_one_id": side_one_id,
                    "side_two_id": side_two_id,
                }
            )
        meets = await self._local_dao.create_meets(insert_data)
        return {meet.sl_id: meet.id for meet in meets}

    async def _create_games(
        self,
        tournament_id: int,
        tournament: TournamentState,
        *,
        sl_sides_map: dict[int, int],
        sl_stages_map: dict[int, int],
        sl_meets_map: dict[int, int],
    ) -> None:
        for sl_game in tournament.games:
            side_one_id = sl_sides_map[sl_game.sl_side_one_id]
            side_two_id = sl_sides_map[sl_game.sl_side_two_id]
            stage_id = sl_stages_map[sl_game.sl_stage_id]
            meet_id = sl_meets_map.get(sl_game.sl_meet_id) if sl_game.sl_meet_id else None
            game_id = await self._local_dao.create_game(
                tournament_id,
                sl_game,
                sl_event=tournament.sl_event,
                side_one_id=side_one_id,
                side_two_id=side_two_id,
                stage_id=stage_id,
                meet_id=meet_id,
            )
            await self._local_dao.create_game_results(game_id)
            await self._local_dao.create_game_sides(game_id, side_ids=(side_one_id, side_two_id))

    async def _load_tournaments(self, tournaments: list[TournamentState]) -> None:
        for tournament in tournaments:
            division = tournament.sl_event.get_division(tournament.sport, name_en=tournament.name_en)
            category_id = tournament.category_id
            if not category_id:
                category_id = await self._local_dao.get_or_create_tournament_category(
                    tournament.sl_category,
                    division=division,
                    conference=tournament.sl_event.conference,
                )
            time_start_id = await self._local_dao.get_or_create_tournament_time(
                tournament.start_at.time(),
                sport=tournament.sport,
            )

            image_url = self._sport_tournament_images.by_category.get(
                category_id
            ) or self._sport_tournament_images.by_sport.get(tournament.sport.value)

            tournament_id, is_exists = await self._local_dao.create_tournament(
                tournament,
                category_id=category_id,
                time_start_id=time_start_id,
                image_url=image_url,
            )
            if is_exists:
                self._logger.warning(f"Турнир с sl_id={tournament.sl_id} уже существует")
                continue
            sl_sides_map = await self._create_tournament_sides(tournament_id, tournament)
            sl_stages_map = await self._create_stages(tournament)
            sl_meets_map = {}
            if tournament.sl_event.is_meets_exists:
                sl_meets_map = await self._create_meets(tournament_id, tournament, sl_sides_map=sl_sides_map)
            await self._create_games(
                tournament_id,
                tournament,
                sl_sides_map=sl_sides_map,
                sl_stages_map=sl_stages_map,
                sl_meets_map=sl_meets_map,
            )

    async def _get_tournaments(  # noqa: CFQ001
        self,
        sl_event: SLImportEvent,
        *,
        future_round_ids: list[int],
        place_row: Row | None,
        sport: SportEnum,
        page: int,
        local_sl_stage_map: dict[int, int],
    ) -> list[TournamentState]:
        limit = self._LOAD_ROUND_PER_PAGE
        offset = page * self._LOAD_ROUND_PER_PAGE
        rounds = await self._implan_dao.get_event_rounds(
            sl_event.id,
            self._round_start_at,
            ignore_sl_ids=future_round_ids,
            limit=limit,
            offset=offset,
        )
        round_ids = [round_.id for round_ in rounds]
        meets_map = await self._implan_dao.get_meets_map(round_ids)
        round_side_ordering_map = await self._implan_dao.get_round_teams_map(round_ids)
        games_map = await self._implan_dao.get_round_games(round_ids)
        round_sides_map: dict[int, set[int]] = defaultdict(set)
        round_all_sides_map: dict[int, set[int]] = defaultdict(set)
        round_stage_map: dict[int, set[int]] = defaultdict(set)
        for game in itertools.chain(*games_map.values()):
            if not sl_event.is_meets_exists:
                round_sides_map[game.round_id].add(game.team_a_id)
                round_sides_map[game.round_id].add(game.team_b_id)
            round_all_sides_map[game.round_id].add(game.team_a_id)
            round_all_sides_map[game.round_id].add(game.team_b_id)
            round_stage_map[game.round_id].add(game.stage_type_id)
        for meet in itertools.chain(*meets_map.values()):
            if sl_event.is_meets_exists:
                round_sides_map[meet.round_id].add(meet.team_a_id)
                round_sides_map[meet.round_id].add(meet.team_b_id)
            round_all_sides_map[meet.round_id].add(meet.team_a_id)
            round_all_sides_map[meet.round_id].add(meet.team_b_id)
        side_ids = set(itertools.chain(*round_all_sides_map.values()))
        sides_map = await self._implan_dao.get_teams(side_ids)
        stage_ids = set(itertools.chain(*round_stage_map.values()))
        stages_map = await self._implan_dao.get_stages(stage_ids)
        tournaments = []
        for round_ in rounds:
            meets = (
                [
                    Meet(
                        sl_id=meet.id,
                        sl_side_one_id=meet.team_a_id,
                        sl_side_two_id=meet.team_b_id,
                        start_at=meet.start_at,
                        sport=sport,
                    )
                    for meet in meets_map[round_.id]
                ]
                if meets_map
                else []
            )
            games = [
                Game(
                    sl_id=game.id,
                    sl_meet_id=game.meet_id,
                    sl_stage_id=game.stage_type_id,
                    sl_side_one_id=game.team_a_id,
                    sl_side_two_id=game.team_b_id,
                    sl_state_id=game.state_id,
                    sport=sport,
                    start_game=game.start_at,
                    finish_game=game.finish_at,
                )
                for game in games_map.get(round_.id, [])
            ]
            sides = {
                side_id: Side(
                    sport=sport,
                    sl_id=sides_map[side_id].id,
                    sl_gender_id=sides_map[side_id].gender_id,
                    title_ru=sides_map[side_id].title_ru,
                    title_en=sides_map[side_id].title_en,
                    sl_type_id=sides_map[side_id].type_id,
                    is_part_of_side=sl_event.is_meets_exists and side_id not in round_sides_map[round_.id],
                )
                for side_id in round_all_sides_map.get(round_.id, [])
                if side_id in sides_map
            }
            try:
                stages = {
                    stage_id: Stage(
                        sl_id=stages_map[stage_id].id,
                        name_ru=stages_map[stage_id].title_ru,
                        name_en=stages_map[stage_id].title_en,
                    )
                    for stage_id in round_stage_map[round_.id]
                }
            except KeyError as exc:
                self._logger.exception(f"Стадия для турнира не найдена: round_id={round_.id}, stage_ids={stage_ids}")
                raise exc

            tournament_state = get_tournament_state(
                round_,
                sl_event=sl_event,
                sport=sport,
                place_row=place_row,
                meets=meets,
                games=games,
                sides=sides,
                sl_side_ids=round_sides_map[round_.id],
                side_ordering_map=round_side_ordering_map[round_.id],
                stages=stages,
                local_sl_stage_map=local_sl_stage_map,
            )
            if tournament_state.is_valid:
                tournaments.append(tournament_state)
        return tournaments

    async def _load_sl_data(
        self,
        sl_events: Iterable[SLImportEvent],
        *,
        sport: SportEnum,
        places_map: dict[int, Row],
        local_sl_stage_map: dict[int, int],
    ) -> None:
        future_round_ids = []
        if self._is_regular:
            future_round_ids = await self._local_dao.get_future_tournament_sl_ids(sport)
        self._logger.info(f"{future_round_ids=}")
        for sl_event in sl_events:
            self._logger.info(f"{sl_event=}")
            place_row = places_map.get(sl_event.place_id) if sl_event.place_id else None
            page = 0
            while True:
                tournaments = await self._get_tournaments(
                    sl_event,
                    future_round_ids=future_round_ids,
                    place_row=place_row,
                    sport=sport,
                    page=page,
                    local_sl_stage_map=local_sl_stage_map,
                )
                self._logger.info(f"{len(tournaments)=}")
                if not tournaments:
                    break
                await self._load_tournaments(tournaments)
                page += 1

    def is_tba(self, sport: SportEnum, name: str | None) -> bool:
        match sport:
            case SportEnum.TABLE_TENNIS | SportEnum.FOOTBALL | SportEnum.VOLLEYBALL | SportEnum.TENNIS:
                return name in SL_TBA_TAGS
            case _:
                return False

    async def _check_update_game(
        self,
        sl_game: Row,
        game: Row,
        *,
        sport: SportEnum,
        sl_event: SLImportEvent,
    ) -> tuple[dict[str, Any], dict[SideEnum, dict[str, Any]]]:
        updated_data = {}
        updated_sides = {}
        if game.side_one_sl_id != sl_game.team_a_id and not self.is_tba(sport, sl_game.team_a_title_en):
            side_info = Side(
                sport=sport,
                sl_id=sl_game.team_a_id,
                sl_type_id=sl_game.team_a_type_id,
                title_ru=sl_game.team_a_title_ru,
                title_en=sl_game.team_a_title_en,
                sl_gender_id=sl_game.team_a_gender_id,
                is_part_of_side=sl_event.is_meets_exists,
            )
            side_id = await self._create_side(sl_game.team_a_id, side_info, sport=sport)
            updated_data["side_one_id"] = side_id
            updated_sides[SideEnum.ONE] = {
                "old_id": game.side_one_id,
                "new_id": side_id,
                "is_tba": game.side_one_is_tba,
            }
        if game.side_two_sl_id != sl_game.team_b_id and not self.is_tba(sport, sl_game.team_a_title_en):
            side_info = Side(
                sport=sport,
                sl_id=sl_game.team_b_id,
                sl_type_id=sl_game.team_b_type_id,
                title_ru=sl_game.team_b_title_ru,
                title_en=sl_game.team_b_title_en,
                sl_gender_id=sl_game.team_b_gender_id,
                is_part_of_side=sl_event.is_meets_exists,
            )
            side_id = await self._create_side(sl_game.team_b_id, side_info, sport=sport)
            updated_data["side_two_id"] = side_id
            updated_sides[SideEnum.TWO] = {
                "old_id": game.side_two_id,
                "new_id": side_id,
                "is_tba": game.side_two_is_tba,
            }
        if game.start_game != sl_game.start_at:
            updated_data["start_game"] = sl_game.start_at
        return updated_data, updated_sides

    async def _update_tournament_sides(
        self,
        tournament_id: int,
        *,
        sport: SportEnum,
        updated_sides_map: dict[SideEnum, dict[str, Any]],
    ) -> None:
        tournament_existing_sides_map = await self._local_dao.get_tournament_side_ids(tournament_id)
        game_existing_side_ids = await self._local_dao.get_games_side_ids(tournament_id)
        on_create_sides = []
        on_delete_sides = []
        on_restore_sides = []
        tba_side_ids = []
        side_ordering_map = {}
        for updated_side in updated_sides_map.values():
            if updated_side["new_id"] in tournament_existing_sides_map:
                if not updated_side["is_tba"] and tournament_existing_sides_map[updated_side["new_id"]].is_deleted:
                    on_restore_sides.append(updated_side["new_id"])
            else:
                on_create_sides.append(updated_side["new_id"])
                if updated_side["is_tba"] and sport != SportEnum.TENNIS:
                    tba_side_ids.append(updated_side["new_id"])

                old_order_by = tournament_existing_sides_map[updated_side["old_id"]].order_by
                side_ordering_map[updated_side["new_id"]] = old_order_by

            if updated_side["old_id"] not in game_existing_side_ids:
                on_delete_sides.append(updated_side["old_id"])
        if on_create_sides:
            side_ratings_map = await self._local_dao.get_side_ratings(datetime.now(), on_create_sides)
            max_tour_number = await self._local_dao.get_max_tour_number(tournament_id)
            await self._local_dao.create_tournament_sides(
                tournament_id,
                on_create_sides,
                tba_side_ids,
                side_ratings_map,
                sport=sport,
                side_ordering_map=side_ordering_map,
            )
            if max_tour_number:
                await self._local_dao.create_tournament_stage_sides(
                    tournament_id,
                    on_create_sides,
                    max_tour_number=max_tour_number,
                    sport=sport,
                    side_ordering_map=side_ordering_map,
                )
        if on_delete_sides:
            await self._local_dao.update_tournament_sides(tournament_id, on_delete_sides, on_delete=True)
        if on_restore_sides:
            await self._local_dao.update_tournament_sides(tournament_id, on_restore_sides, on_delete=False)

    async def _update_sides_count(self, tournament_ids: Iterable[int]) -> None:
        await self._local_dao.update_sides_count(tournament_ids)

    async def _check_game_updates(
        self, sl_events: Iterable[SLImportEvent], *, sport: SportEnum, last_updated_at: datetime
    ) -> set[int]:
        sl_events_map = {sl_event.id: sl_event for sl_event in sl_events}
        sl_games = await self._implan_dao.get_last_updated_games(sl_events_map.keys(), last_updated_at=last_updated_at)
        translation_ids = [game.id for game in sl_games]
        games_map = await self._local_dao.get_games_by_sl_id(translation_ids)

        tournaments_ids = set()
        for sl_game in sl_games:
            sl_event = sl_events_map[sl_game.event_id]
            if game := games_map.get(sl_game.id):
                updated_data, updated_sides = await self._check_update_game(
                    sl_game,
                    game,
                    sport=sport,
                    sl_event=sl_event,
                )
                if updated_data:
                    await self._local_dao.update_game(game.id, updated_data)
                if updated_sides:
                    await self._local_dao.update_game_sides(game.id, updated_sides_map=updated_sides)
                    if not sl_event.is_meets_exists:
                        await self._update_tournament_sides(
                            game.tournament_id,
                            sport=sport,
                            updated_sides_map=updated_sides,
                        )
                    tournaments_ids.add(game.tournament_id)

        return tournaments_ids

    async def _check_update_tournament(
        self,
        sl_tournament_state: TournamentState,
        tournament: Row,
        *,
        sl_event: SLImportEvent,
    ) -> dict[str, Any]:
        updated_data: dict[str, Any] = {}
        new_event_id = sl_tournament_state.sl_category.event.sl_id if sl_tournament_state.sl_category.event else None
        new_league_id = sl_tournament_state.sl_category.league.sl_id if sl_tournament_state.sl_category.league else None
        if (tournament.event_sl_id and tournament.event_sl_id != new_event_id) or (
            tournament.league_sl_id and tournament.league_sl_id != new_league_id
        ):
            updated_data["category_id"] = await self._local_dao.get_or_create_tournament_category(
                sl_tournament_state.sl_category,
                division=sl_event.get_division(tournament.sport_id, name_en=sl_tournament_state.name_en),
                conference=sl_event.conference,
            )
        if tournament.name_ru != sl_tournament_state.name_ru:
            updated_data["name_ru"] = sl_tournament_state.name_ru
        if tournament.name_en != sl_tournament_state.name_en:
            updated_data["name_en"] = sl_tournament_state.name_en
        if tournament.start_at != sl_tournament_state.start_at:
            updated_data["start_at"] = sl_tournament_state.start_at
        if tournament.end_date_at != sl_tournament_state.finish_at:
            updated_data["end_date_at"] = sl_tournament_state.finish_at
        return updated_data

    async def _check_tournament_updates(
        self,
        sl_events: Iterable[SLImportEvent],
        *,
        places_map: dict[int, Row],
        last_updated_at: datetime,
    ) -> None:
        sl_event_map = {sl_event.id: sl_event for sl_event in sl_events}
        sl_rounds = await self._implan_dao.get_last_updated_rounds(sl_event_map.keys(), last_updated_at=last_updated_at)
        sl_rounds_ids = [sl_round.id for sl_round in sl_rounds]
        tournaments_map = await self._local_dao.get_tournaments_by_sl_id(sl_rounds_ids)
        for sl_round in sl_rounds:
            if tournament := tournaments_map.get(sl_round.id):
                sl_event = sl_event_map[sl_round.event_id]
                place_row = places_map[sl_event.place_id] if sl_event.place_id else None
                tournament_state = get_tournament_state(
                    sl_round,
                    sl_event=sl_event,
                    sport=tournament.sport_id,
                    place_row=place_row,
                )
                updated_data = await self._check_update_tournament(tournament_state, tournament, sl_event=sl_event)
                if updated_data:
                    await self._local_dao.update_tournament(tournament.id, updated_data)

    async def _join_basketball_tournaments(self) -> None:
        base_tournaments = await self._local_dao.get_not_joined_basketball_tournaments()
        throw_tournaments = await self._local_dao.get_not_joined_throw_tournaments()
        joined_tournaments_map = join_basketball_tournaments(base_tournaments, throw_tournaments)
        not_joined_games = await self._local_dao.get_not_joined_games(joined_tournaments_map.keys())
        not_joined_meets = await self._local_dao.get_not_joined_meets(joined_tournaments_map.values())
        joined_meet_games_map = join_basketball_games(
            not_joined_games,
            not_joined_meets,
            joined_tournaments_map=joined_tournaments_map,
            related_sides=self._basketball_related_sides,
        )
        if joined_tournaments_map:
            await self._local_dao.join_tournaments(joined_tournaments_map)
        if joined_meet_games_map:
            await self._local_dao.join_meet_games(joined_meet_games_map)

    async def run(self) -> None:
        start_at = datetime.now()
        last_updated_at = await self._get_last_updated_at()
        places_map = await self._local_dao.get_places_map()
        group_stages_map = await self._local_dao.get_group_stages_by_sports()

        if self._sport:
            sl_events: Iterable[SLImportEvent] = self._sl_events_map[self._sport]
            if self._sl_event_ids:
                sl_events = [sl_event for sl_event in sl_events if sl_event.id in self._sl_event_ids]
            await self._load_sl_data(
                sl_events, sport=self._sport, places_map=places_map, local_sl_stage_map=group_stages_map[self._sport]
            )
        else:
            updated_tournaments_ids = set()
            for sport, sl_events in self._sl_events_map.items():
                self._logger.info(f"{sport=}")

                await self._load_sl_data(
                    sl_events, sport=sport, places_map=places_map, local_sl_stage_map=group_stages_map[sport]
                )
                updated_tournaments_ids.update(
                    await self._check_game_updates(sl_events, sport=sport, last_updated_at=last_updated_at)
                )
                await self._check_tournament_updates(
                    sl_events,
                    places_map=places_map,
                    last_updated_at=last_updated_at,
                )
            if updated_tournaments_ids:
                await self._update_sides_count(updated_tournaments_ids)
            await self._set_last_updated_at(start_at)
        await self._join_basketball_tournaments()
