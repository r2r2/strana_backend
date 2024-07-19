import operator
import re
from dataclasses import dataclass, field
from datetime import datetime, timezone

from portal_liga_pro_db import ConferenceEnum, DivisionEnum, GenderEnum

from sdk.db.enums import SideTypesEnum, SportEnum, TournamentStateEnum

_sl_title_regex = re.compile(r"(?P<team_name>.+) \((?P<nickname>.+)\)")
_TENNIS_CATEGORIES_MAP = {
    "Tournament А. 45+": 25,
    "Tournament А": 24,
    "Tournament B. 45+": 27,
    "Tournament B": 26,
    "Tournament V. 45+": 29,
    "Tournament V": 28,
    "Tournament G. 45+": 31,
    "Tournament G": 30,
    "Tournament D. 45+": 33,
    "Tournament D": 32,
    "Tournament E. 45+": 35,
    "Tournament E": 34,
}
_BASKETBALL_CATEGORIES_MAP = {
    "Tournament A": 94,
    "Tournament B": 95,
    "Tournament V": 96,
}
_VOLLEYBALL_CATEGORIES_MAP = {
    "Tournament A": 92,
    "Tournament B": 93,
}
_CATEGORIES_SPORT_MAP = {
    SportEnum.TENNIS: _TENNIS_CATEGORIES_MAP,
    SportEnum.BASKETBALL: _BASKETBALL_CATEGORIES_MAP,
    SportEnum.VOLLEYBALL: _VOLLEYBALL_CATEGORIES_MAP,
}

SL_TBA_TAGS = ("The final", "3rd place", "Team is not defined", "TBA", "", None)


@dataclass
class SLImportEvent:
    id: int
    divisions: list[DivisionEnum] = field(default_factory=list)
    conference: ConferenceEnum | None = None
    place_id: int | None = None
    type_id: int | None = None
    is_meets_exists: bool = False
    is_part_another: bool = False
    is_hide: bool = True

    def get_division(self, sport: SportEnum, *, name_en: str) -> DivisionEnum | None:
        if len(self.divisions) == 1:
            return self.divisions[0]
        division = None
        title = name_en.lower()
        if sport == SportEnum.E_FOOTBALL:
            if "gold" in title:
                division = DivisionEnum.GOLD
            else:
                division = DivisionEnum.ELITE
        elif sport == SportEnum.E_BASKETBALL:
            if "ruby" in title:
                division = DivisionEnum.RUBY
            elif "amethyst" in title:
                division = DivisionEnum.AMETHYST
            else:
                division = DivisionEnum.DIAMOND
        return division


@dataclass
class Stage:
    sl_id: int
    name_ru: str
    name_en: str


@dataclass
class Side:
    sport: SportEnum
    sl_id: int
    sl_type_id: int | None
    sl_gender_id: int | None
    title_ru: str
    title_en: str
    nickname: str | None = None
    team_name_ru: str | None = None
    team_name_en: str | None = None
    is_tba: bool = False
    is_part_of_side: bool = False

    def __post_init__(self) -> None:
        if self.title_en in SL_TBA_TAGS:
            self.title_ru = "Команда не определена"
            self.title_en = "TBA"
            self.nickname = "TBA"
            self.team_name_ru = "Команда не определена"
            self.team_name_en = "TBA"
            self.is_tba = True
        elif self.sport in (SportEnum.E_FOOTBALL, SportEnum.E_BASKETBALL, SportEnum.E_HOCKEY):
            title_ru_match = _sl_title_regex.match(self.title_ru)
            title_en_match = _sl_title_regex.match(self.title_en)
            if title_ru_match and title_en_match:
                self.nickname = title_en_match.group("nickname")
                self.team_name_ru = title_ru_match.group("team_name")
                self.team_name_en = title_en_match.group("team_name")
            else:
                self.nickname = self.title_en
                self.team_name_ru = self.title_ru
                self.team_name_en = self.title_en

    @property
    def side_type(self) -> SideTypesEnum:
        if self.sport in (SportEnum.TENNIS, SportEnum.TABLE_TENNIS):
            return SideTypesEnum.PLAYERS
        elif self.sport in (SportEnum.VOLLEYBALL, SportEnum.BASKETBALL, SportEnum.FOOTBALL, SportEnum.HOCKEY):
            return SideTypesEnum.TEAMS
        elif self.sport in (SportEnum.E_FOOTBALL, SportEnum.E_BASKETBALL, SportEnum.E_HOCKEY):
            return SideTypesEnum.TEAMS_PLAYERS
        raise Exception()


@dataclass
class Meet:
    sl_id: int
    sl_side_one_id: int
    sl_side_two_id: int
    start_at: datetime
    sport: SportEnum


@dataclass
class Game:
    sl_id: int
    sl_meet_id: int | None
    sl_stage_id: int
    sl_side_one_id: int
    sl_side_two_id: int
    sl_state_id: int
    sport: SportEnum
    start_game: datetime
    finish_game: datetime


@dataclass
class Place:
    id: int
    short_name_ru: str
    short_name_en: str


@dataclass
class SLLeague:
    sl_id: int
    name_ru: str
    name_en: str


@dataclass
class SLEvent:
    sl_id: int
    name_ru: str
    name_en: str


@dataclass
class SLCategory:
    sport: SportEnum
    name_ru: str = field(init=False)
    name_en: str = field(init=False)
    event: SLEvent | None
    league: SLLeague | None
    gender: GenderEnum

    def __post_init__(self) -> None:
        if self.sport == SportEnum.TABLE_TENNIS and self.league:
            self.name_ru = self.league.name_ru
            self.name_en = self.league.name_en
            self.event = None
        elif self.event:
            self.name_ru = self.event.name_ru
            self.name_en = self.event.name_en
            self.league = None


@dataclass
class TournamentState:
    sl_id: int
    sl_event: SLImportEvent
    name_ru: str
    name_en: str
    place: Place | None
    sl_category: SLCategory
    sport: SportEnum
    gender: GenderEnum
    start_at: datetime
    finish_at: datetime
    meets: list[Meet]
    games: list[Game]
    sides: dict[int, Side]
    sl_side_ids: set[int]
    side_ordering_map: dict[int, int]
    stages: dict[int, Stage]
    has_group_stage: bool | None
    max_tour_number: int | None

    def __post_init__(self) -> None:
        if not self.finish_at:
            last_game = sorted(self.games, key=operator.attrgetter("finish_game"))[-1]
            self.finish_at = last_game.finish_game
        if self.sport == SportEnum.TABLE_TENNIS and self.place and self.sl_category.league:
            self.name_ru = f"Турнир {self.place.short_name_ru}. Лига {self.sl_category.league.name_ru}"
            self.name_en = f"Tournament {self.place.short_name_en}. League {self.sl_category.league.name_en}"

    @property
    def state(self) -> TournamentStateEnum:
        now = datetime.now(tz=timezone.utc)
        if now > self.finish_at:
            return TournamentStateEnum.FINISHED
        elif now > self.start_at:
            return TournamentStateEnum.LIVE
        return TournamentStateEnum.ANNOUNCE

    @property
    def sides_count(self) -> int:
        return len([side for side in self.sides.values() if not side.is_tba])

    @property
    def is_valid(self) -> bool:
        conditions = [
            self.sides_count > 1,
            self.games,
        ]

        if self.sl_event.is_meets_exists:
            conditions.append(
                self.meets and all(meet.sl_side_one_id and meet.sl_side_two_id for meet in self.meets),
            )
        return all(conditions)

    @property
    def category_id(self) -> int | None:
        if categories_map := _CATEGORIES_SPORT_MAP.get(self.sport):
            for name_en, tournament_category_id in categories_map.items():
                if name_en in self.name_en:
                    return tournament_category_id
        return None
