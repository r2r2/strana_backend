from datetime import date, datetime, time

from sdk.db.schemas import PeriodScoresType
from sdk.schemas.base import JSONBaseModel


class Team(JSONBaseModel):
    old_id: int
    old_lp_id: int | None
    sl_id: int | None
    team_captain_id: int | None
    name_ru: str | None
    name_en: str | None
    short_name_ru: str | None
    short_name_en: str | None
    search_field: str
    gender_id: int | None
    city_id: int | None
    phone: str | None
    rating: float | None


class Player(JSONBaseModel):
    old_id: int
    old_lp_id: int | None
    fntr_id: int | None
    sl_id: int | None
    first_name_ru: str | None
    first_name_en: str | None
    surname_ru: str | None
    surname_en: str | None
    patronymic_ru: str | None
    patronymic_en: str | None
    short_name_ru: str | None
    short_name_en: str | None
    nickname: str | None
    search_field: str
    email: str | None
    phone: str | None
    birthday: date | None
    gender_id: int | None
    rating: float | None
    rating_date: date | None


class Side(JSONBaseModel):
    old_id: int
    sl_id: int | None
    type_id: int
    team: Team | None
    player: Player | None


class TournamentSide(JSONBaseModel):
    old_id: int
    old_side_id: int
    place: int | None
    auto_place: int | None
    rating_before: float | None
    rating_after: float | None
    delta: float | None
    date_reg: datetime | None


class TournamentStageSide(JSONBaseModel):
    old_id: int
    tour_number: int
    old_side_id: int
    place: int | None


class Game(JSONBaseModel):
    old_id: int
    old_lp_id: int
    sl_id: int | None
    stage_old_lp_id: int
    start_game: datetime
    old_side_one_id: int
    old_side_two_id: int
    youtube: str | None
    score_one: int | None
    score_two: int | None
    period_scores: PeriodScoresType | None
    duration: int | None


class TournamentState(JSONBaseModel):
    old_id: int
    old_lp_id: int
    sl_id: int | None
    sport_id: int
    place_old_lp_id: int | None
    category_id: int
    gender_id: int
    side_type_id: int
    start_at: datetime
    end_date_at: date | None
    name_ru: str
    name_en: str
    address: str | None
    text_ru: str | None
    text_en: str | None
    youtube: str | None
    sides: list[Side]
    tournament_sides: list[TournamentSide]
    tournament_stage_sides: list[TournamentStageSide]
    games: list[Game]

    @property
    def time_start(self) -> time:
        return self.start_at.time()
