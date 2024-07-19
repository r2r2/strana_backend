import enum
from datetime import datetime

from boilerplates.sentry import SentrySettings
from portal_liga_pro_db import SportEnum
from sl_slack_logger import SlackConfig

from jobs.import_sl_games.schemas import SLImportEvent
from sdk.dynaconf_settings import DynaconfSettings
from sdk.internal.app_settings import (
    LoggingSettings,
    PostgresSettings,
    RabbitSettings,
    RedisSettings,
    RegisteredQueuesSettings,
)
from .fields import CronTab


class ImportLPDumpTypeEnum(enum.IntEnum):
    ALL = 1
    RATING = 2
    FIX_PARTICIPANTS = 3


class BaseJobSettings(DynaconfSettings):
    schedule: float | CronTab
    run_at_startup: bool = False


class BaseImportFromSLJobSettings(BaseJobSettings):
    is_preview: bool


class HistoryImportFromSLJobSettings(BaseImportFromSLJobSettings):
    sport_id: int
    created_date_from: datetime
    created_date_to: datetime


class RegularImportFromSLJobSettings(BaseImportFromSLJobSettings):
    pass


class ImportGamesFromSLSettings(BaseJobSettings):
    created_date_from: datetime | None
    last_updated_hours: int


class HistoryImportGamesFromSLSettings(BaseJobSettings):
    created_date_from: datetime | None
    last_updated_hours: int
    sport: SportEnum | None = None
    sl_event_ids: list[int] | None = None


class CalculateParticipantStatsSettings(BaseJobSettings):
    sport_ids: list[int]
    is_throw_player: bool = False


class RecalculateRatingSettings(BaseJobSettings):
    sport_id: int
    from_start_at: datetime
    to_start_at: datetime


class ImportLPDumpSettings(BaseJobSettings):
    import_type: ImportLPDumpTypeEnum
    tournament_start_at: datetime
    tournament_end_at: datetime
    sport_id: SportEnum
    load_tournaments_count: int


class UpdateTeamRatingsJobSettings(BaseJobSettings):
    players_sport_ids: list[int] | None
    team_sport_ids: list[int] | None


class CalcTournamentsStatsJobSettings(BaseJobSettings):
    sport_ids: list[int]
    from_start_at: datetime
    to_start_at: datetime


class RegisteredJobs(DynaconfSettings):
    history_import_from_sl: HistoryImportFromSLJobSettings | None
    regular_import_from_sl: RegularImportFromSLJobSettings | None
    import_games_from_sl: ImportGamesFromSLSettings | None
    recalculate_rating: RecalculateRatingSettings | None
    clear_import_data: BaseJobSettings | None
    history_import_games_from_sl: HistoryImportGamesFromSLSettings | None
    calculate_participant_stats: CalculateParticipantStatsSettings | None
    import_lp_dump: ImportLPDumpSettings | None
    update_team_players_ratings: UpdateTeamRatingsJobSettings | None
    calculate_tournaments_stats: CalcTournamentsStatsJobSettings | None
    update_nicknames_from_sl: BaseJobSettings | None


class JobSettings(DynaconfSettings):
    app_name: str
    escape_logs: bool
    debug: bool


class TournamentImagesSettings(DynaconfSettings):
    by_sport: dict[int, str]
    by_category: dict[int, str]


class Settings(DynaconfSettings):
    environment: str
    job: JobSettings
    postgres: PostgresSettings
    sl_implan_postgres: PostgresSettings
    lp_dump_postgres: PostgresSettings
    rabbit: RabbitSettings
    redis: RedisSettings
    registered_jobs: RegisteredJobs
    registered_queues: RegisteredQueuesSettings
    sentry: SentrySettings
    sport_tournament_images: TournamentImagesSettings
    basketball_related_sides: dict[int, int]
    sl_events: dict[SportEnum, list[SLImportEvent]]
    slack: SlackConfig
    logging: LoggingSettings
