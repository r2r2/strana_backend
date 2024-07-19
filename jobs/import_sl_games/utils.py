from datetime import date

from portal_liga_pro_db import GenderEnum, SportEnum
from sqlalchemy.engine import Row

from jobs.types import JoinGamesMap
from .schemas import (
    Game,
    Meet,
    Place,
    Side,
    SLCategory,
    SLEvent,
    SLImportEvent,
    SLLeague,
    Stage,
    TournamentState,
)


def join_basketball_tournaments(
    base_tournaments: dict[int, dict[date, Row]],
    throw_tournaments: dict[int, dict[date, Row]],
) -> dict[int, int]:
    joined_tournaments_map = {}
    for category_id, base_tournaments_map in base_tournaments.items():
        for base_tournament in base_tournaments_map.values():
            if category_id in throw_tournaments and base_tournament.start_at in throw_tournaments[category_id]:
                throw_tournament = throw_tournaments[category_id].get(base_tournament.start_at)
                if throw_tournament:
                    joined_tournaments_map[base_tournament.id] = throw_tournament.id
    return joined_tournaments_map


def join_basketball_games(
    not_joined_games: dict[int, JoinGamesMap],
    not_joined_meets: dict[int, JoinGamesMap],
    *,
    joined_tournaments_map: dict[int, int],
    related_sides: dict[int, int],
) -> dict[int, int]:
    reversed_related_sides = {v: k for k, v in related_sides.items()}
    meet_games_map = {}
    for base_tournament_id, throw_tournament_id in joined_tournaments_map.items():
        for meet_key, meet in not_joined_meets[throw_tournament_id].items():
            game_key = (reversed_related_sides[meet_key[0]], reversed_related_sides[meet_key[1]])
            meet_games_map[meet.id] = not_joined_games[base_tournament_id][game_key].id
    return meet_games_map


def get_tournament_state(
    sl_round: Row,
    *,
    sl_event: SLImportEvent,
    sport: SportEnum,
    place_row: Row | None,
    meets: list[Meet] | None = None,
    games: list[Game] | None = None,
    sides: dict[int, Side] | None = None,
    sl_side_ids: set[int] | None = None,
    side_ordering_map: dict[int, int] | None = None,
    stages: dict[int, Stage] | None = None,
    local_sl_stage_map: dict[int, int] | None = None,
) -> TournamentState:
    gender = GenderEnum(sl_round.gender_id) if sl_round.gender_id else GenderEnum.MIXED
    place = Place(**place_row) if place_row else None
    event = SLEvent(
        sl_id=sl_round.event_id,
        name_ru=sl_round.event_title_ru,
        name_en=sl_round.event_title_en,
    )
    league = (
        SLLeague(
            sl_id=sl_round.league_id,
            name_ru=sl_round.league_title_ru,
            name_en=sl_round.league_title_en,
        )
        if sl_round.league_id
        else None
    )

    has_group_stage = None
    max_tour_number = None
    if stages and local_sl_stage_map:
        max_tour_number = 0
        for stage in stages:
            if has_group_stage is None and stage in local_sl_stage_map:
                has_group_stage = True
            if (tour_number := local_sl_stage_map.get(stage)) and tour_number > max_tour_number:
                max_tour_number = tour_number

    return TournamentState(
        sl_id=sl_round.id,
        sl_event=sl_event,
        name_ru=sl_round.title_ru,
        name_en=sl_round.title_en,
        sport=sport,
        gender=gender,
        start_at=sl_round.start_at,
        finish_at=sl_round.finish_at,
        place=place,
        sl_category=SLCategory(
            sport=sport,
            event=event,
            league=league,
            gender=sl_round.gender_id,
        ),
        meets=meets or [],
        games=games or [],
        sides=sides or {},
        sl_side_ids=sl_side_ids or set(),
        side_ordering_map=side_ordering_map or {},
        stages=stages or {},
        has_group_stage=has_group_stage,
        max_tour_number=max_tour_number,
    )
