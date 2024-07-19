from datetime import datetime, timedelta, timezone

import orjson
from aio_pika import Message

from jobs.base import BaseJob
from jobs.calc_tournaments_stat.service import CalculateTournamentsStatsService
from jobs.calculate_player_stats.service import CalculateParticipantStatsService
from jobs.clear_import_data.service import ClearImportDataService
from jobs.import_lp_dump.service import ImportLPDumpService
from jobs.import_sl_games.service import ImportSLGamesService
from jobs.internal.app_settings import (
    BaseJobSettings,
    CalcTournamentsStatsJobSettings,
    CalculateParticipantStatsSettings,
    HistoryImportFromSLJobSettings,
    HistoryImportGamesFromSLSettings,
    ImportGamesFromSLSettings,
    ImportLPDumpSettings,
    RecalculateRatingSettings,
    RegularImportFromSLJobSettings,
    UpdateTeamRatingsJobSettings,
)
from jobs.update_nicknames.service import UpdateNicknameService
from jobs.utils import create_app
from sdk.db.dao.team_ratings import TeamPlayersRatingsDAO
from sdk.enums import ImporterTypeEnum, RecalculateRatingType

celery_app = create_app()


@celery_app.register_task
class HistoryImportFromSL(BaseJob[HistoryImportFromSLJobSettings]):
    name = "history_import_from_sl"
    description = "Загрузка исторических данных о событиях игр из SL"

    async def _run_async(self) -> None:
        sport_id = getattr(self, "_sport_id", self.job_settings.sport_id)
        from_start_date = getattr(self, "_from_start_date", self.job_settings.created_date_from)
        to_start_date = getattr(self, "_to_start_date", self.job_settings.created_date_to)
        is_preview = getattr(self, "_is_preview", self.job_settings.is_preview)
        message_body = Message(
            body=orjson.dumps(
                {
                    "importer_type": ImporterTypeEnum.HISTORY,
                    "sport_id": sport_id,
                    "from_start_date": from_start_date.replace(tzinfo=timezone.utc),
                    "to_start_date": to_start_date.replace(tzinfo=timezone.utc),
                    "is_preview": is_preview,
                }
            )
        )
        await self._channel.default_exchange.publish(
            message_body,
            routing_key=self._settings.registered_queues.importer_sl.name,
        )


@celery_app.register_task
class RegularImportFromSL(BaseJob[RegularImportFromSLJobSettings]):
    name = "regular_import_from_sl"
    description = "Загрузка регулярных данных о событиях игр из SL"

    async def _run_async(self) -> None:
        start_date_to = datetime.now(timezone.utc).replace(microsecond=0)
        start_date_from = start_date_to - timedelta(days=1)
        message_body = Message(
            body=orjson.dumps(
                {
                    "importer_type": ImporterTypeEnum.REGULAR,
                    "from_start_date": start_date_from,
                    "to_start_date": start_date_to,
                    "is_preview": self.job_settings.is_preview,
                }
            )
        )
        await self._channel.default_exchange.publish(
            message_body,
            routing_key=self._settings.registered_queues.importer_sl.name,
        )


@celery_app.register_task
class ImportGamesFromSL(BaseJob[ImportGamesFromSLSettings]):
    name = "import_games_from_sl"
    description = "Импорт игр из SL"

    async def _run_async(self) -> None:
        async with (self._session_maker() as session, self._sl_implan_session_maker() as sl_session):
            async with session.begin():
                importer = ImportSLGamesService(
                    self.job_settings.created_date_from,
                    self.job_settings.last_updated_hours,
                    is_regular=True,
                    session=session,
                    sl_session=sl_session,
                    redis=self._redis,
                    logger=self._logger,
                )
                await importer.run()


@celery_app.register_task
class HistoryImportGamesFromSL(BaseJob[HistoryImportGamesFromSLSettings]):
    name = "history_import_games_from_sl"
    description = "Импорт игр из SL"

    async def _run_async(self) -> None:
        async with (self._session_maker() as session, self._sl_implan_session_maker() as sl_session):
            async with session.begin():
                importer = ImportSLGamesService(
                    self.job_settings.created_date_from,
                    self.job_settings.last_updated_hours,
                    is_regular=False,
                    session=session,
                    sl_session=sl_session,
                    redis=self._redis,
                    logger=self._logger,
                    sport=self.job_settings.sport,
                    sl_event_ids=self.job_settings.sl_event_ids,
                )
                await importer.run()


@celery_app.register_task
class UpdateTeamPlayersRatings(BaseJob[UpdateTeamRatingsJobSettings]):
    name = "update_team_players_ratings"
    description = "Обновление рейтинга команд и игроков"

    async def _run_async(self) -> None:
        async with self._session_maker() as session:
            async with session.begin():
                dao = TeamPlayersRatingsDAO(session)
                if self.job_settings.team_sport_ids:
                    await dao.update_new_ratings_for_teams(self.job_settings.team_sport_ids)
                if self.job_settings.players_sport_ids:
                    await dao.update_delta_rating_for_players(self.job_settings.players_sport_ids)


@celery_app.register_task
class CalculateParticipantStats(BaseJob[CalculateParticipantStatsSettings]):
    name = "calculate_participant_stats"
    description = "Расчет статистики игроков"

    async def _run_async(self) -> None:
        async with self._session_maker() as session:
            service = CalculateParticipantStatsService(self._settings, session, self._channel, self._logger)
            await service.run(self.job_settings.sport_ids, self.job_settings.is_throw_player)


@celery_app.register_task
class ClearImportData(BaseJob[BaseJobSettings]):
    name = "clear_import_data"
    description = "Очистить данные для импорта"

    async def _run_async(self) -> None:
        async with self._session_maker() as session:
            async with session.begin():
                service = ClearImportDataService(session, self._logger)
                await service.run()


@celery_app.register_task
class ImportLPDump(BaseJob[ImportLPDumpSettings]):
    name = "import_lp_dump"
    description = "Импорт дампа из LP"

    async def _run_async(self) -> None:
        async with (self._session_maker() as session, self._lp_dump_session_maker() as lp_dump_session):
            importer = ImportLPDumpService(self.job_settings, session, lp_dump_session, self._redis, self._logger)
            await importer.run()


@celery_app.register_task
class CalculateTournamentsStats(BaseJob[CalcTournamentsStatsJobSettings]):
    name = "calculate_tournaments_stats"
    description = "Расчет очков и прочей статистики для турнира"

    async def _run_async(self) -> None:
        async with self._session_maker() as session:
            async with session.begin():
                service = CalculateTournamentsStatsService(self._settings, session, self._channel, self._logger)
                await service.run(
                    self.job_settings.sport_ids, self.job_settings.from_start_at, self.job_settings.to_start_at
                )


@celery_app.register_task
class UpdateNicknamesFromSL(BaseJob[BaseJobSettings]):
    name = "update_nicknames_from_sl"
    description = "Обновление никнеймов"

    async def _run_async(self) -> None:
        async with (self._session_maker() as session, self._sl_implan_session_maker() as sl_session):
            async with session.begin():
                service = UpdateNicknameService(
                    session=session,
                    sl_session=sl_session,
                    logger=self._logger,
                )
                await service.update()


@celery_app.register_task
class RecalculateRating(BaseJob[RecalculateRatingSettings]):
    name = "recalculate_rating"
    description = "Обновление рейтинга"

    async def _run_async(self) -> None:
        message_body = Message(
            body=orjson.dumps(
                {
                    "run_type": RecalculateRatingType.HISTORY,
                    "sport_id": self.job_settings.sport_id,
                    "date_start_at": self.job_settings.from_start_at.replace(tzinfo=timezone.utc),
                    "date_end_at": self.job_settings.to_start_at.replace(tzinfo=timezone.utc),
                }
            )
        )
        await self._channel.default_exchange.publish(
            message_body,
            routing_key=self._settings.registered_queues.recalculate_ratings.name,
        )
