import logging
from datetime import datetime

import orjson
from aio_pika import Message
from aio_pika.abc import AbstractChannel
from structlog.typing import FilteringBoundLogger

from jobs.internal.app_settings import Settings
from sdk.db.session import AsyncSession
from .dao import LocalDAO


class CalculateTournamentsStatsService:
    def __init__(
        self,
        settings: Settings,
        session: AsyncSession,
        rabbit_channel: AbstractChannel,
        logger: FilteringBoundLogger,
    ) -> None:
        self._settings = settings
        self._dao = LocalDAO(session)
        self._logger = logger
        self._rabbit_channel = rabbit_channel
        logging.basicConfig()

    async def _call_queue(self, tournament_id: int) -> None:
        message_data = {"tournament_id": tournament_id}
        message_body = Message(body=orjson.dumps(message_data))
        await self._rabbit_channel.default_exchange.publish(
            message_body,
            routing_key=self._settings.registered_queues.tournament_statistic.name,
        )

    async def run(self, sport_ids: list[int], from_start_at: datetime, to_start_at: datetime) -> None:
        for tournament_id in await self._dao.get_tournaments_by_sport(
            sport_ids=sport_ids, from_start_at=from_start_at, to_start_at=to_start_at
        ):
            await self._call_queue(tournament_id)
