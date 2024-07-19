from collections import defaultdict
from collections.abc import Iterable
from datetime import date, datetime, time, timedelta
from typing import Any

from portal_liga_pro_db import Places, PlayerRatings
from portal_liga_pro_db.meets import Meets
from sqlalchemy import (
    Date,
    Integer,
    case,
    cast,
    column,
    func,
    insert,
    select,
    update,
    values,
)
from sqlalchemy.engine import Row
from sqlalchemy.orm import aliased
from sqlalchemy.sql import Values

from jobs.import_sl_games.schemas import (
    Game,
    SLCategory,
    SLImportEvent,
    Stage,
    TournamentState,
)
from jobs.types import JoinGamesMap
from sdk.db.dao.base import BaseDAO
from sdk.db.enums import (
    ConferenceEnum,
    DivisionEnum,
    GameStateEnum,
    GenderEnum,
    SideEnum,
    SideTypesEnum,
    SportEnum,
    StageTypeEnum,
)
from sdk.db.models import (
    GameResults,
    Games,
    GameSides,
    Players,
    Sides,
    Stages,
    Teams,
    TournamentCategories,
    Tournaments,
    TournamentSides,
    TournamentStageSides,
    TournamentTimes,
)
from sdk.enums import TournamentTypeEnum


class LocalDAO(BaseDAO):
    _SL_STATE_MAP = {
        1: GameStateEnum.ANNOUNCE,
        2: GameStateEnum.LIVE,
        3: GameStateEnum.LIVE,
        4: GameStateEnum.LIVE,
        5: GameStateEnum.FINISHED,
        6: GameStateEnum.CANCELED,
        7: GameStateEnum.CANCELED,
    }
    _SL_STAGES_MAP = {
        1: StageTypeEnum.FINAL,
        13: StageTypeEnum.GROUP,
        14: StageTypeEnum.SEMI_FINAL,
        15: StageTypeEnum.SEMI_FINAL,
        16: StageTypeEnum.THIRD_PLACE,
    }

    @staticmethod
    def _get_joined_values_data(joined_ids_map: dict[int, int]) -> Values:
        values_data = [(main_id, other_id) for main_id, other_id in joined_ids_map.items()]
        return values(
            column("main_id", Integer),
            column("other_id", Integer),
            name="values",
        ).data(values_data)

    @staticmethod
    def _split_name(name: str) -> tuple[str | None, str | None, str | None, str]:
        names = dict(enumerate(name.split(" ")))
        surname = names[0]
        first_name = names.get(1)
        patronymic_name = names.get(2)
        short_name = surname
        if first_name and patronymic_name:
            short_name = f"{short_name} {first_name[0]}. {patronymic_name[0]}."
        elif first_name:
            short_name = f"{short_name} {first_name[0]}."
        return surname, first_name, patronymic_name, short_name

    @classmethod
    def _get_full_name_player_data(cls, name_ru: str, name_en: str) -> dict[str, str | None]:
        surname_ru, first_name_ru, patronymic_ru, short_name_ru = cls._split_name(name_ru)
        surname_en, first_name_en, patronymic_en, short_name_en = cls._split_name(name_en)
        return {
            "surname_ru": surname_ru,
            "surname_en": surname_en,
            "first_name_ru": first_name_ru,
            "first_name_en": first_name_en,
            "patronymic_ru": patronymic_ru,
            "patronymic_en": patronymic_en,
            "short_name_ru": short_name_ru,
            "short_name_en": short_name_en,
        }

    @classmethod
    def _get_nickname_player_data(cls, name_en: str) -> dict[str, str]:
        return {
            "nickname": name_en,
            "short_name_ru": name_en,
            "short_name_en": name_en,
        }

    async def get_or_create_tournament_category(
        self,
        sl_category: SLCategory,
        *,
        division: DivisionEnum | None,
        conference: ConferenceEnum | None,
    ) -> int:
        event_sl_id = sl_category.event.sl_id if sl_category.event else None
        league_sl_id = sl_category.league.sl_id if sl_category.league else None
        query = (
            select(TournamentCategories.id)
            .select_from(TournamentCategories)
            .where(
                TournamentCategories.event_sl_id == event_sl_id,
                TournamentCategories.league_sl_id == league_sl_id,
                TournamentCategories.sport_id == sl_category.sport,
                TournamentCategories.division_id == division,
            )
        )
        category_id = await self._get_scalar_or_none(query)
        if not category_id:
            query = (
                insert(TournamentCategories)
                .values(
                    event_sl_id=event_sl_id,
                    league_sl_id=league_sl_id,
                    sport_id=sl_category.sport,
                    conference_id=conference,
                    division_id=division,
                    name_ru=sl_category.name_ru,
                    name_en=sl_category.name_en,
                    gender_id=sl_category.gender,
                )
                .returning(TournamentCategories.id)
            )
            category_id = await self._get_scalar_one(query)
        return category_id  # type: ignore

    async def get_or_create_tournament_time(self, start_time: time, *, sport: SportEnum) -> int:
        query = (
            select(TournamentTimes.id)
            .select_from(TournamentTimes)
            .where(
                TournamentTimes.time == start_time,
                TournamentTimes.sport_id == sport,
            )
        )
        time_id = await self._get_scalar_or_none(query)
        if not time_id:
            query = (
                insert(TournamentTimes)
                .values(
                    sport_id=sport,
                    time=start_time,
                )
                .returning(TournamentTimes.id)
            )
            time_id = await self._get_scalar_one(query)
        return time_id  # type: ignore

    async def create_tournament(
        self,
        tournament: TournamentState,
        *,
        category_id: int,
        time_start_id: int,
        image_url: str | None,
    ) -> tuple[int, bool]:
        query = select(Tournaments.id).select_from(Tournaments).where(Tournaments.sl_id == tournament.sl_id)
        tournament_id = await self._get_scalar_or_none(query)
        is_exists = True
        if not tournament_id:
            sides_count = len(tournament.sl_side_ids) if tournament.meets else tournament.sides_count
            query = (
                insert(Tournaments)
                .values(
                    sl_id=tournament.sl_id,
                    place_id=tournament.sl_event.place_id,
                    sport_id=tournament.sport,
                    organizer_id=1,
                    category_id=category_id,
                    gender_id=tournament.gender,
                    type_id=tournament.sl_event.type_id,
                    side_type_id=tournament.sport.side_type,
                    start_at=tournament.start_at,
                    time_start_id=time_start_id,
                    end_date_at=tournament.finish_at,
                    name_ru=tournament.name_ru,
                    name_en=tournament.name_en,
                    state=tournament.state,
                    sides_count=sides_count,
                    matches_count=len(tournament.games),
                    image_url=image_url,
                    is_hide=tournament.sl_event.is_hide or tournament.sl_event.is_part_another,
                    is_part_another=tournament.sl_event.is_part_another,
                    search_field=func.concat_ws("|", tournament.sl_id, tournament.name_ru),
                )
                .returning(Tournaments.id)
            )
            tournament_id = await self._get_scalar_one(query)
            is_exists = False
        return tournament_id, is_exists

    async def get_sl_sides(self, sl_side_ids: Iterable[int], sport: SportEnum) -> dict[int, int]:
        query = (
            select(Sides.id, Sides.sl_id)
            .select_from(Sides)
            .where(Sides.sl_id.in_(sl_side_ids), Sides.sport_id == sport)
        )
        rows = await self._fetch_all(query)
        return {row.sl_id: row.id for row in rows}

    async def get_sl_stages(self, sl_stage_ids: Iterable[int], *, sport: SportEnum) -> dict[int, int]:
        query = (
            select(Stages.id, Stages.sl_id)
            .select_from(Stages)
            .where(Stages.sl_id.in_(sl_stage_ids), Stages.sport_id == sport)
        )
        rows = await self._fetch_all(query)
        return {row.sl_id: row.id for row in rows}

    async def get_or_create_team(
        self,
        name_ru: str,
        name_en: str,
        sl_id: int,
        sl_gender_id: int | None,
        *,
        sport: SportEnum,
    ) -> int:
        query = (
            select(Teams.id)
            .select_from(Teams)
            .where(
                Teams.sl_id == sl_id,
                Teams.sport_id == sport,
            )
        )
        team_id = await self._get_scalar_or_none(query)
        if not team_id:
            query = (
                insert(Teams)
                .values(
                    sl_id=sl_id,
                    sport_id=sport,
                    name_ru=name_ru,
                    name_en=name_en,
                    short_name_ru=name_ru,
                    short_name_en=name_en,
                    search_field="null",
                    gender_id=sl_gender_id,
                )
                .returning(Teams.id)
            )
            team_id = await self._get_scalar_one(query)
            query = (
                update(Teams)
                .where(Teams.id == team_id)
                .values(search_field=func.concat_ws("|", Teams.id, Teams.sl_id, Teams.name_ru, Teams.name_en))
            )
            await self._execute(query)
        return team_id  # type: ignore

    async def get_or_create_cyber_team(self, name_ru: str, name_en: str, *, sport: SportEnum) -> int:
        query = (
            select(Teams.id)
            .select_from(Teams)
            .where(
                Teams.name_ru == name_ru,
                Teams.name_en == name_en,
                Teams.sport_id == sport,
            )
        )
        team_id = await self._get_scalar_or_none(query)
        if not team_id:
            query = (
                insert(Teams)
                .values(
                    sport_id=sport,
                    name_ru=name_ru,
                    name_en=name_en,
                    short_name_ru=name_ru,
                    short_name_en=name_en,
                    search_field="null",
                    gender_id=GenderEnum.MALE,
                )
                .returning(Teams.id)
            )
            team_id = await self._get_scalar_one(query)
            query = (
                update(Teams)
                .where(Teams.id == team_id)
                .values(search_field=func.concat(Teams.id, "|", Teams.sl_id, "|", Teams.name_ru))
            )
            await self._execute(query)
        return team_id  # type: ignore

    async def get_or_create_player(
        self,
        name_ru: str,
        name_en: str,
        sl_id: int,
        sl_gender_id: int | None,
        *,
        sport: SportEnum,
    ) -> int:
        query = (
            select(
                Players.id,
                func.concat_ws(" ", Players.surname_ru, Players.first_name_ru, Players.patronymic_ru).label("name_ru"),
                func.concat_ws(" ", Players.surname_en, Players.first_name_en, Players.patronymic_en).label("name_en"),
            )
            .select_from(Players)
            .where(
                Players.sl_id == sl_id,
                Players.sport_id == sport,
            )
        )
        player_info = await self._fetch_one(query)

        if player_info:
            local_player_full_name = self._get_full_name_player_data(player_info.name_ru, player_info.name_en)
            sl_player_full_name = self._get_full_name_player_data(name_ru, name_en)

            if local_player_full_name != sl_player_full_name:
                search_field = func.concat_ws("|", player_info.id, sl_id, name_ru, name_en)
                update_query = (
                    update(Players)
                    .values(**sl_player_full_name, search_field=search_field)
                    .where(Players.sl_id == sl_id)
                )
                await self._execute(update_query)

            return player_info.id  # type: ignore

        rating = 0 if sport in (SportEnum.TENNIS, SportEnum.TABLE_TENNIS) else None
        search_field_list = [Players.id, Players.sl_id]
        insert_data: dict[str, str | Any]
        if sport == SportEnum.BASKETBALL:
            insert_data = self._get_nickname_player_data(name_en)
            search_field_list.append(Players.nickname)
        else:
            insert_data = self._get_full_name_player_data(name_ru, name_en)
            search_field_list.extend(
                (
                    func.concat_ws(" ", Players.surname_ru, Players.first_name_ru, Players.patronymic_ru),
                    func.concat_ws(" ", Players.surname_en, Players.first_name_en, Players.patronymic_en),
                )
            )
        query = (
            insert(Players)
            .values(
                sl_id=sl_id,
                sport_id=sport,
                search_field="null",
                gender_id=sl_gender_id,
                rating=rating,
                **insert_data,
            )
            .returning(Players.id)
        )
        player_id = await self._get_scalar_one(query)
        query = (
            update(Players).where(Players.id == player_id).values(search_field=func.concat_ws("|", *search_field_list))
        )
        await self._execute(query)
        return player_id  # type: ignore

    async def get_or_create_cyber_player(self, nickname: str, *, sport: SportEnum) -> int:
        query = (
            select(Players.id)
            .select_from(Players)
            .where(
                Players.nickname == nickname,
                Players.sport_id == sport,
            )
        )
        player_id = await self._get_scalar_or_none(query)
        if not player_id:
            insert_data = self._get_nickname_player_data(nickname)
            query = (
                insert(Players)
                .values(
                    sport_id=sport,
                    search_field="null",
                    gender_id=GenderEnum.MALE,
                    **insert_data,
                )
                .returning(Players.id)
            )
            player_id = await self._get_scalar_one(query)
            query = (
                update(Players)
                .where(Players.id == player_id)
                .values(
                    search_field=func.concat(
                        Players.id,
                        "|",
                        Players.sl_id,
                        "|",
                        Players.nickname,
                    )
                )
            )
            await self._execute(query)
        return player_id  # type: ignore

    async def get_or_create_side(
        self,
        sl_side_id: int,
        team_id: int | None,
        player_id: int | None,
        side_type: SideTypesEnum,
        is_tba: bool,
        *,
        sport: SportEnum,
    ) -> int:
        query = select(Sides.id).select_from(Sides).where(Sides.sl_id == sl_side_id, Sides.sport_id == sport)
        side_id = await self._get_scalar_or_none(query)
        if not side_id:
            query = (
                insert(Sides)
                .values(
                    sl_id=sl_side_id,
                    sport_id=sport,
                    type_id=side_type,
                    team_id=team_id,
                    player_id=player_id,
                    is_tba=is_tba,
                )
                .returning(Sides.id)
            )
            side_id = await self._get_scalar_one(query)
        return side_id  # type: ignore

    async def get_max_tour_number(self, tournament_id: int) -> int | None:
        query = (
            select(func.max(Stages.tour_number))
            .select_from(Games)
            .join(Stages, Games.stage_id == Stages.id)
            .where(
                Games.tournament_id == tournament_id,
                Stages.type == StageTypeEnum.GROUP,
            )
        )
        return await self._get_scalar_or_none(query)

    async def get_side_ratings(self, start_at: datetime, side_ids: Iterable[int]) -> dict[int, float]:
        query = (
            select(Sides.id, PlayerRatings.rating)
            .distinct(Sides.id)
            .select_from(PlayerRatings)
            .join(Sides, PlayerRatings.player_id == Sides.player_id)
            .where(Sides.id.in_(side_ids), PlayerRatings.date_at < start_at, PlayerRatings.deleted_at.is_(None))
            .order_by(Sides.id, PlayerRatings.date_at.desc(), PlayerRatings.created_at.desc())
        )
        rows = await self._fetch_all(query)
        return {row.id: row.rating for row in rows}

    async def create_tournament_sides(
        self,
        tournament_id: int,
        side_ids: Iterable[int],
        tba_side_ids: Iterable[int],
        side_ratings_map: dict[int, float],
        *,
        sport: SportEnum,
        side_ordering_map: dict[int, int] | None = None,
    ) -> None:
        if side_ordering_map is None:
            side_ordering_map = {}
        values = [
            {
                "tournament_id": tournament_id,
                "side_id": side_id,
                "sport_id": sport,
                "order_by": side_ordering_map.get(side_id),
                "rating_before": side_ratings_map.get(side_id),
                "deleted_at": func.now() if side_id in tba_side_ids else None,
            }
            for side_id in side_ids
        ]
        query = insert(TournamentSides).values(values)
        await self._execute(query)

    async def update_tournament_sides(self, tournament_id: int, side_ids: Iterable[int], *, on_delete: bool) -> None:
        deleted_at = func.now() if on_delete else None
        query = (
            update(TournamentSides)
            .where(TournamentSides.tournament_id == tournament_id, TournamentSides.side_id.in_(side_ids))
            .values(deleted_at=deleted_at)
        )
        await self._execute(query)
        query = (
            update(TournamentStageSides)
            .where(TournamentStageSides.tournament_id == tournament_id, TournamentStageSides.side_id.in_(side_ids))
            .values(deleted_at=deleted_at)
        )
        await self._execute(query)

    async def create_tournament_stage_sides(
        self,
        tournament_id: int,
        side_ids: Iterable[int],
        *,
        max_tour_number: int,
        sport: SportEnum,
        side_ordering_map: dict[int, int] | None = None,
    ) -> None:
        if side_ordering_map is None:
            side_ordering_map = {}
        values = [
            {
                "tournament_id": tournament_id,
                "side_id": side_id,
                "sport_id": sport,
                "tour_number": tour_number,
                "order_by": side_ordering_map.get(side_id),
            }
            for side_id in side_ids
            for tour_number in range(1, max_tour_number + 1)
        ]
        query = insert(TournamentStageSides).values(values)
        await self._execute(query)

    async def get_or_create_stage(self, stage_info: Stage, *, sport: SportEnum) -> int:
        query = select(Stages.id).select_from(Stages).where(Stages.sl_id == stage_info.sl_id, Stages.sport_id == sport)
        stage_id = await self._get_scalar_or_none(query)
        if not stage_id:
            query = (
                insert(Stages)
                .values(
                    sl_id=stage_info.sl_id,
                    sport_id=sport,
                    type=self._SL_STAGES_MAP.get(stage_info.sl_id, StageTypeEnum.GROUP),
                    tour_number=1,
                    name_ru=stage_info.name_ru,
                    name_en=stage_info.name_en,
                )
                .returning(Stages.id)
            )
            stage_id = await self._get_scalar_one(query)
        return stage_id  # type: ignore

    async def create_meets(self, insert_data: list[dict[str, Any]]) -> list[Row]:
        query = insert(Meets).values(insert_data).returning(Meets.id, Meets.sl_id)
        return await self._fetch_all(query)

    async def create_game(
        self,
        tournament_id: int,
        game_info: Game,
        *,
        sl_event: SLImportEvent,
        side_one_id: int,
        side_two_id: int,
        stage_id: int,
        meet_id: int | None,
    ) -> int:
        query = (
            insert(Games)
            .values(
                sl_id=game_info.sl_id,
                sport_id=game_info.sport,
                tournament_id=tournament_id,
                stage_id=stage_id,
                start_game=game_info.start_game,
                state=GameStateEnum.ANNOUNCE if game_info.sl_state_id < 6 else GameStateEnum.CANCELED,
                side_one_id=side_one_id,
                side_two_id=side_two_id,
                meet_id=meet_id,
                is_hide=sl_event.is_hide or sl_event.is_part_another,
                is_part_another=sl_event.is_part_another,
                is_doubles=1,
            )
            .returning(Games.id)
        )
        return await self._get_scalar_one(query)  # type: ignore

    async def create_game_results(self, game_id: int) -> None:
        query = insert(GameResults).values(game_id=game_id)
        await self._execute(query)

    async def create_game_sides(self, game_id: int, *, side_ids: Iterable[int]) -> None:
        values = [{"game_id": game_id, "side_id": side_id} for side_id in side_ids]
        query = insert(GameSides).values(values)
        await self._execute(query)

    async def get_game_sl_id(self, game_id: int) -> int:
        query = select(Games.sl_id).select_from(Games).where(Games.id == game_id)
        return await self._get_scalar_one(query)  # type: ignore

    async def get_games_by_sl_id(self, translation_ids: Iterable[int]) -> dict[int, Row]:
        side_one_table = aliased(Sides)
        side_two_table = aliased(Sides)
        query = (
            select(
                Games.id,
                Games.sl_id,
                Games.tournament_id,
                Games.side_one_id,
                Games.side_two_id,
                side_one_table.sl_id.label("side_one_sl_id"),
                side_one_table.is_tba.label("side_one_is_tba"),
                side_two_table.sl_id.label("side_two_sl_id"),
                side_two_table.is_tba.label("side_two_is_tba"),
                Stages.sl_id.label("stage_sl_id"),
                Games.start_game,
                Games.state,
            )
            .select_from(Games)
            .join(Stages, Games.stage_id == Stages.id)
            .join(side_one_table, Games.side_one_id == side_one_table.id)
            .join(side_two_table, Games.side_two_id == side_two_table.id)
            .where(Games.sl_id.in_(translation_ids))
        )
        rows = await self._fetch_all(query)
        return {row.sl_id: row for row in rows}

    async def get_tournaments_by_sl_id(self, round_ids: Iterable[int]) -> dict[int, Row]:
        query = (
            select(
                Tournaments.id,
                Tournaments.sl_id,
                Tournaments.sport_id,
                Tournaments.name_ru,
                Tournaments.name_en,
                Tournaments.start_at,
                Tournaments.end_date_at,
                TournamentCategories.event_sl_id,
                TournamentCategories.league_sl_id,
            )
            .select_from(Tournaments)
            .join(TournamentCategories, Tournaments.category_id == TournamentCategories.id)
            .where(Tournaments.sl_id.in_(round_ids))
        )
        rows = await self._fetch_all(query)
        return {row.sl_id: row for row in rows}

    async def update_game(self, game_id: int, updated_data: dict[str, Any]) -> None:
        query = update(Games).values(**updated_data).where(Games.id == game_id)
        await self._execute(query)

    async def update_tournament(self, tournament_id: int, updated_data: dict[str, Any]) -> None:
        if "name_ru" in updated_data:
            updated_data["search_field"] = func.concat_ws("|", Tournaments.sl_id, updated_data["name_ru"])
        query = update(Tournaments).values(**updated_data).where(Tournaments.id == tournament_id)
        await self._execute(query)

    async def get_tournament_side_ids(self, tournament_id: int) -> dict[int, Row]:
        query = (
            select(
                TournamentSides.side_id,
                TournamentSides.order_by,
                case((TournamentSides.deleted_at.is_(None), False), else_=True).label("is_deleted"),
            )
            .select_from(TournamentSides)
            .where(TournamentSides.tournament_id == tournament_id)
        )
        rows = await self._fetch_all(query)
        return {row.side_id: row for row in rows}

    async def get_games_side_ids(self, tournament_id: int) -> list[int]:
        query = (
            select(GameSides.side_id.distinct())
            .select_from(GameSides)
            .join(Games, GameSides.game_id == Games.id)
            .where(Games.tournament_id == tournament_id)
        )
        return await self._get_scalars(query)

    async def update_game_sides(self, game_id: int, *, updated_sides_map: dict[SideEnum, dict[str, Any]]) -> None:
        query = select(GameSides.id, GameSides.side_id).select_from(GameSides).where(GameSides.game_id == game_id)
        game_sides = await self._fetch_all(query)
        game_sides_map = {game_side.side_id: game_side.id for game_side in game_sides}
        if len(game_sides_map) == 1:
            updated_sides = {
                game_sides[side.value - 1].id: updated_sides_map[side]["new_id"]
                for side in SideEnum
                if updated_sides_map.get(side)
            }
        else:
            updated_sides = {
                game_sides_map[updated_sides_map[side]["old_id"]]: updated_sides_map[side]["new_id"]
                for side in SideEnum
                if updated_sides_map.get(side)
            }
        case_expression = case(
            *[(GameSides.id == game_side_id, new_side_id) for game_side_id, new_side_id in updated_sides.items()]
        )
        query = (
            update(GameSides)
            .values(side_id=case_expression)
            .where(GameSides.game_id == game_id, GameSides.id.in_(updated_sides.keys()))
        )
        await self._execute(query)

    async def get_places_map(self) -> dict[int, Row]:
        query = select(Places.id, Places.short_name_ru, Places.short_name_en).select_from(Places)
        rows = await self._fetch_all(query)
        return {row.id: row for row in rows}

    async def get_future_tournament_sl_ids(self, sport: SportEnum) -> list[int]:
        query = (
            select(Tournaments.sl_id)
            .select_from(Tournaments)
            .where(Tournaments.sport_id == sport, Tournaments.start_at > func.now(), Tournaments.sl_id.is_not(None))
        )
        return await self._get_scalars(query)

    async def get_not_joined_football_tournaments(self, event_sl_id: int, is_main: bool) -> dict[date, Row]:
        query = (
            select(Tournaments.id, cast(Tournaments.start_at, Date).label("start_at"))
            .select_from(Tournaments)
            .join(TournamentCategories, Tournaments.category_id == TournamentCategories.id)
            .where(
                TournamentCategories.event_sl_id == event_sl_id,
                Tournaments.is_history.is_(False),
                Tournaments.created_at > datetime.now() - timedelta(days=1),
            )
            .order_by(Tournaments.start_at)
        )
        if is_main:
            query = query.where(Tournaments.next_tournament_part_id.is_(None))
        rows = await self._fetch_all(query)
        return {row.start_at: row for row in rows}

    async def get_not_joined_games(self, tournament_ids: Iterable[int]) -> dict[int, JoinGamesMap]:
        query = (
            select(Games.id, Games.tournament_id, Games.side_one_id, Games.side_two_id)
            .select_from(Games)
            .where(Games.tournament_id.in_(tournament_ids))
            .order_by(Games.start_game)
        )
        rows = await self._fetch_all(query)
        games_map: dict[int, dict[tuple[int, int], Row]] = {}
        for row in rows:
            game_key = (row.side_one_id, row.side_two_id)
            games_map.setdefault(row.tournament_id, {})[game_key] = row
        return games_map

    async def get_not_joined_meets(self, tournament_ids: Iterable[int]) -> dict[int, JoinGamesMap]:
        query = (
            select(Meets.id, Meets.tournament_id, Meets.side_one_id, Meets.side_two_id)
            .select_from(Meets)
            .where(Meets.tournament_id.in_(tournament_ids))
            .order_by(Meets.start_at)
        )
        rows = await self._fetch_all(query)
        meets_map: dict[int, dict[tuple[int, int], Row]] = {}
        for row in rows:
            game_key = (row.side_one_id, row.side_two_id)
            meets_map.setdefault(row.tournament_id, {})[game_key] = row
        return meets_map

    async def get_not_joined_basketball_tournaments(self) -> dict[int, dict[date, Row]]:
        query = (
            select(Tournaments.id, Tournaments.category_id, cast(Tournaments.start_at, Date).label("start_at"))
            .select_from(Tournaments)
            .where(
                Tournaments.sport_id == SportEnum.BASKETBALL,
                Tournaments.type_id == TournamentTypeEnum.BASE,
                Tournaments.next_tournament_part_id.is_(None),
                Tournaments.created_at > datetime.now() - timedelta(days=14),
            )
            .order_by(Tournaments.start_at)
        )
        rows = await self._fetch_all(query)
        throw_tournaments: dict[int, dict[date, Row]] = defaultdict(dict)
        for row in rows:
            throw_tournaments[row.category_id][row.start_at] = row
        return throw_tournaments

    async def get_not_joined_throw_tournaments(self) -> dict[int, dict[date, Row]]:
        throw_tournaments = aliased(Tournaments)
        base_tournaments = aliased(Tournaments)
        query = (
            select(
                throw_tournaments.id,
                throw_tournaments.category_id,
                cast(throw_tournaments.start_at, Date).label("start_at"),
            )
            .select_from(throw_tournaments)
            .join(base_tournaments, throw_tournaments.id == base_tournaments.next_tournament_part_id, isouter=True)
            .where(
                throw_tournaments.sport_id == SportEnum.BASKETBALL,
                throw_tournaments.type_id == TournamentTypeEnum.MEETS,
                base_tournaments.next_tournament_part_id.is_(None),
                throw_tournaments.created_at > datetime.now() - timedelta(days=14),
            )
            .order_by(throw_tournaments.start_at)
        )
        rows = await self._fetch_all(query)
        throw_tournaments_map: dict[int, dict[date, Row]] = defaultdict(dict)
        for row in rows:
            throw_tournaments_map[row.category_id][row.start_at] = row
        return throw_tournaments_map

    async def join_tournaments(self, joined_tournaments_map: dict[int, int]) -> None:
        values_expression = self._get_joined_values_data(joined_tournaments_map)
        query = (
            update(Tournaments)
            .values(next_tournament_part_id=values_expression.c.other_id)
            .where(Tournaments.id == values_expression.c.main_id)
        )
        await self._execute(query, synchronize_session=False)

    async def join_games(self, joined_games_map: dict[int, int]) -> None:
        values_expression = self._get_joined_values_data(joined_games_map)
        query = (
            update(Games)
            .values(next_game_part_id=values_expression.c.other_id)
            .where(Games.id == values_expression.c.main_id)
        )
        await self._execute(query, synchronize_session=False)

    async def join_meet_games(self, joined_meet_games_map: dict[int, int]) -> None:
        values_expression = self._get_joined_values_data(joined_meet_games_map)
        query = (
            update(Meets)
            .values(main_game_id=values_expression.c.other_id)
            .where(Meets.id == values_expression.c.main_id)
        )
        await self._execute(query, synchronize_session=False)

    async def get_group_stages_by_sports(self) -> dict[int, dict[int, int]]:
        query = select(Stages.sl_id, Stages.sport_id, Stages.tour_number).where(Stages.type == StageTypeEnum.GROUP)
        result = await self._fetch_all(query)
        group_stages_map: dict[int, dict[int, int]] = defaultdict(dict)

        for stage in result:
            group_stages_map[stage.sport_id][stage.sl_id] = stage.tour_number

        return group_stages_map

    async def update_sides_count(self, tournament_ids: Iterable[int]) -> None:
        query = (
            select(TournamentSides.tournament_id, func.count().label("sides_count"))
            .select_from(TournamentSides)
            .where(
                TournamentSides.tournament_id.in_(tournament_ids),
                TournamentSides.deleted_at.is_(None),
            )
            .group_by(TournamentSides.tournament_id)
        )
        main_query = (
            update(Tournaments)
            .where(Tournaments.id == query.c.tournament_id, Tournaments.sides_count != query.c.sides_count)
            .values(sides_count=query.c.sides_count)
        )
        await self._execute(main_query, synchronize_session=False)
