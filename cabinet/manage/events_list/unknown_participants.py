from copy import copy
from typing import Any

import structlog
from tortoise import Tortoise

from config import tortoise_config
from src.events_list.repos import EventListRepo, EventParticipantListRepo, EventParticipantList, EventList
from src.users.repos import UserRepo


class CheckParticipantsNotInDB:
    def __init__(self):
        self.event_list_repo: EventListRepo = EventListRepo()
        self.event_participant_list_repo: EventParticipantListRepo = EventParticipantListRepo()
        self.user_repo: UserRepo = UserRepo()
        self.logger = structlog.get_logger(self.__class__.__name__)

        self.orm_class: type[Tortoise] = Tortoise
        self.orm_config: dict[str, Any] = copy(tortoise_config)
        self.orm_config.pop("generate_schemas", None)

    def __await__(self):
        return self().__await__()

    async def __call__(self, *args):
        await self.orm_class.init(config=self.orm_config)
        self.logger.info("Запущен скрипт для проверки участников мероприятий в БД")
        not_found_users: dict[str, list] = {}
        if args is not None and args[0] != "-a":
            event_id: int = int(args[0])
            filters: dict[str, Any] = dict(event_id=event_id)
        else:
            filters: dict[str, Any] = {}
        events: list[EventList] = await self.event_list_repo.list(
            filters=filters,
        )
        self.logger.info(f'Список мероприятий: {events}')
        for event in events:
            not_found_users.setdefault(event.name, [])
            participants: list[EventParticipantList] = await self.event_participant_list_repo.list(
                filters=dict(event=event),
            )
            for participant in participants:
                if not await self._check_user_exists(participant=participant):
                    if participant.phone not in not_found_users[event.name]:
                        not_found_users[event.name].append(participant.phone)

        self.logger.info(f'Список не найденных пользователей: {not_found_users}')
        self.logger.info("Завершен скрипт для проверки участников мероприятий в БД")
        await self.orm_class.close_connections()

    async def _check_user_exists(self, participant: EventParticipantList) -> bool:
        user: dict[str, Any] | None = await self.user_repo.retrieve(
            filters=dict(phone=participant.phone),
        ).values('id')
        if not user:
            return False
        return True
