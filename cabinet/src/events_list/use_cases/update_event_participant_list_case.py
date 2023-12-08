import asyncio
from typing import Awaitable, Any

from tortoise.transactions import atomic

from common.depreg import DepregAPI
from common.depreg.dto.depreg_response import DepregParticipantsDTO, DepregGroupDTO
from common.utils import parse_phone
from src.events_list.entities import BaseEventListCase
from src.events_list.exceptions import EventListNotFoundError
from src.events_list.repos import (
    EventListRepo,
    EventParticipantListRepo,
    EventList,
    EventParticipantList,
    EventGroupRepo,
    EventGroup,
)
from src.notifications.repos import OnboardingRepo, Onboarding
from src.users.repos import UserRepo


class UpdateEventParticipantListCase(BaseEventListCase):
    """
    Кейс обновления списка участников мероприятия по кнопке в админке.
    """

    qr_code_slug = 'qr_code'

    def __init__(
        self,
        event_list_repo: type[EventListRepo],
        event_participant_list_repo: type[EventParticipantListRepo],
        event_group_repo: type[EventGroupRepo],
        onboarding_repo: type[OnboardingRepo],
        user_repo: type[UserRepo],
        depreg_api: type[DepregAPI],
    ):
        self.event_list_repo: EventListRepo = event_list_repo()
        self.event_participant_list_repo: EventParticipantListRepo = event_participant_list_repo()
        self.event_group_repo: EventGroupRepo = event_group_repo()
        self.onboarding_repo: OnboardingRepo = onboarding_repo()
        self.user_repo: UserRepo = user_repo()
        self.depreg_api: type[DepregAPI] = depreg_api

    async def __call__(self, event_id: int) -> None:
        event: EventList = await self.event_list_repo.retrieve(filters=dict(event_id=event_id))
        if not event:
            raise EventListNotFoundError

        participants: DepregParticipantsDTO = await self.get_participants(event_id=event_id, token=event.token)
        timeslots: dict[int, str | None] = await self.get_timeslots(token=event.token, participants=participants)

        event_group_data: list[dict[str, Any]] = []
        groups_no_duplicates: set[int] = set()
        phone_list: list[str] = []
        event_group_data: list[dict[str, Any]] = []
        groups_no_duplicates: set[int] = set()
        phone_list: list[str] = []
        event_group_data: list[dict[str, Any]] = []
        groups_no_duplicates: set[int] = set()
        phone_list: list[str] = []
        for participant in participants.data:
            if not (phone := await self.validate_phone(phone=participant.phone)):
                continue

            phone_list.append(phone)

            timeslot: str | None = self._get_timeslot(timeslots=timeslots, group_id=participant.group_id)

            data: dict[str, Any] = dict(
                phone=phone,
                event=event,
                code=participant.code,
                group_id=participant.group_id,
                timeslot=timeslot,
            )
            if p_list := await self._get_participant_list(event=event, phone=participant.phone):
                await self.event_participant_list_repo.update(model=p_list, data=data)
            else:
                await self.event_participant_list_repo.create(data=data)

            if participant.group_id in groups_no_duplicates:
                # Проверка на дубликаты групп
                continue
            groups_no_duplicates.add(participant.group_id)
            event_group_data.append(
                {
                    "group_id": participant.group_id,
                    "timeslot": timeslot,
                    "event": event,
                }
            )

            if participant.group_id in groups_no_duplicates:
                # Проверка на дубликаты групп
                continue
            groups_no_duplicates.add(participant.group_id)
            event_group_data.append(
                {
                    "group_id": participant.group_id,
                    "timeslot": timeslot,
                    "event": event,
                }
            )

        await self.full_onboarding_users(slug=self.qr_code_slug, phone_list=phone_list)
        await self.save_event_group_data(event_group_data=event_group_data)
        await self.full_onboarding_users(slug=self.qr_code_slug, phone_list=phone_list)

    async def get_participants(self, event_id: int, token: str) -> DepregParticipantsDTO:
        async with self.depreg_api() as depreg:
            response: DepregParticipantsDTO = await depreg.get_participants(event_id=event_id, token=token)
        return response

    async def get_timeslots(
        self,
        token: str,
        participants: DepregParticipantsDTO,
    ) -> dict[int, str]:

        group_ids: set[int] = {participant.group_id for participant in participants.data}

        async with self.depreg_api() as depreg:
            async_queries: list[Awaitable] = []
            for group_id in group_ids:
                async_queries.append(
                    depreg.get_group_by_id(group_id=group_id, token=token)
                )
            result_queries: tuple[DepregGroupDTO] = await asyncio.gather(*async_queries)

        timeslots: dict[int, str | None] = {
            result.id: result.timeslot for result in result_queries
        }
        return timeslots

    def _get_timeslot(self, timeslots: dict[int, str | None], group_id: int) -> str | None:
        if timeslots.get(group_id):
            timeslot: str = timeslots[group_id].split("-")[0]
        else:
            timeslot: str | None = timeslots[group_id]
        return timeslot

    async def _get_participant_list(self, event: EventList, phone: str) -> EventParticipantList | None:
        return await self.event_participant_list_repo.retrieve(filters=dict(event=event, phone=phone))

    async def validate_phone(self, phone: str | None) -> str | None:
        if not phone:
            return
        return parse_phone(phone)

    async def save_event_group_data(self, event_group_data: list[dict[str, Any]]) -> None:
        async_tasks: list[Awaitable] = []
        for data in event_group_data:
            async_tasks.append(
                self.__save_event_group_data(data)
            )
        await asyncio.gather(*async_tasks)

    @atomic(connection_name='cabinet')
    async def __save_event_group_data(self, data: dict[str, Any]) -> None:
        filters: dict[str, Any] = dict(
            group_id=data['group_id'],
        )
        data: dict[str, Any] = dict(
            group_id=data['group_id'],
            timeslot=data['timeslot'],
            event=data['event'],
        )
        event_group: EventGroup = await self.event_group_repo.retrieve(filters=filters)
        if event_group:
            await self.event_group_repo.update(model=event_group, data=data)
        else:
            await self.event_group_repo.create(data=data)

    async def full_onboarding_users(self, slug: str, phone_list: list[str]):
        filters = dict(
            phone__in=phone_list,
        )
        users = await self.user_repo.list(filters=filters)

        filters = dict(
            slug=slug,
        )
        onboarding: Onboarding = await self.onboarding_repo.retrieve(filters=filters)

        await onboarding.user.add(*users)
