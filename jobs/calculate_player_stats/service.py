import logging

import orjson
from aio_pika import Message
from aio_pika.abc import AbstractChannel
from portal_liga_pro_db import SideTypesEnum, SportEnum
from structlog.typing import FilteringBoundLogger

from jobs.internal.app_settings import Settings
from sdk.db.session import AsyncSession
from .dao import LocalDAO


class CalculateParticipantStatsService:
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

    async def _call_queue(self, participant_id: int, sport_id: int, is_throw_player: bool) -> None:
        message_data = {"participant_id": participant_id, "sport_id": sport_id, "is_throw_player": is_throw_player}
        message_body = Message(body=orjson.dumps(message_data))
        await self._rabbit_channel.default_exchange.publish(
            message_body,
            routing_key=self._settings.registered_queues.team_player_statistic.name,
        )

    async def run(self, sport_ids: list[int], is_throw_player: bool) -> None:
        for sport_id in sport_ids:
            sport = SportEnum(sport_id)
            if is_throw_player or sport.side_type == SideTypesEnum.PLAYERS:
                participant_ids = await self._dao.get_player_ids(sport_id)
            elif sport.side_type == SideTypesEnum.TEAMS:
                participant_ids = await self._dao.get_team_ids(sport_id)
            else:
                raise Exception()
            for participant_id in participant_ids:
                await self._call_queue(participant_id, sport_id, is_throw_player)
