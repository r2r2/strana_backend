import asyncio
import random
from typing import Any, Optional

import structlog

from common.amocrm import AmoCRM
from common.amocrm.constants import AmoContactQueryWith
from common.amocrm.types import AmoContact, AmoLead
from common.redis import Redis, broker as redis
from common.utils import partition_list
from src.amocrm.repos import AmocrmPipeline
from src.booking.repos import Booking
from src.cities.repos import City
from src.users.constants import UserPinningStatusType
from src.users.entities import BaseUserService
from src.users.exceptions import UserNotFoundError
from src.users.repos import (
    PinningStatusRepo,
    PinningStatus,
    UserPinningStatusRepo,
    User,
    UserRepo,
    UniqueStatus,
)
from src.users.utils import get_unique_status


class TokenBucketRateLimiter:
    _instance = None

    def __new__(cls, max_tokens: int, refill_rate: float):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.__init__(max_tokens, refill_rate)
        return cls._instance

    def __init__(self, max_tokens: int, refill_rate: float):
        self.max_tokens: int = max_tokens
        self.refill_rate: float = refill_rate
        self.tokens: int = max_tokens
        self.last_refill_time: float = asyncio.get_event_loop().time()
        self.lock: asyncio.Lock = asyncio.Lock()
        self.redis: Redis = redis

    async def _refill(self) -> None:
        now: float = asyncio.get_event_loop().time()
        time_passed: float = now - self.last_refill_time
        new_tokens: float = time_passed * self.refill_rate

        # Fetch the tokens from Redis
        stored_tokens = await self.redis.get('token_bucket_tokens')
        if stored_tokens is not None:
            self.tokens: int = int(stored_tokens)

        self.tokens: float = min(self.tokens + new_tokens, self.max_tokens)
        self.last_refill_time: float = now

        # Store the tokens in Redis
        await self.redis.set('token_bucket_tokens', self.tokens, expire=60 * 60)

    async def acquire(self, num_tokens: int = 1) -> bool:
        async with self.lock:
            await self._refill()
            if num_tokens <= self.tokens:
                self.tokens -= num_tokens

                # Store the updated tokens in Redis
                await self.redis.set('token_bucket_tokens', self.tokens, expire=60 * 60)

                return True

            return False

    async def wait_and_acquire(self, num_tokens: int = 1, timeout: Optional[float] = None) -> bool:
        sleep_time = 1 / self.refill_rate

        while True:
            if await self.acquire(num_tokens):
                return True

            await asyncio.sleep(sleep_time)

            if timeout is not None:
                timeout -= sleep_time
                if timeout <= 0:
                    return False

            # Back off exponentially
            sleep_time *= 2
            sleep_time += random.uniform(0, 1)  # Add random jitter to the sleep time


class CheckPinningStatusService(BaseUserService):
    """
    Проверка на закрепление
    todo: deprecated
    """
    def __init__(
        self,
        user_repo: type[UserRepo],
        check_pinning_repo: type[PinningStatusRepo],
        user_pinning_repo: type[UserPinningStatusRepo],
        amocrm_class: type[AmoCRM],
        amocrm_config: dict[Any, Any],
    ):
        self.user_repo: UserRepo = user_repo()
        self.check_pinning_repo: PinningStatusRepo = check_pinning_repo()
        self.user_pinning_repo: UserPinningStatusRepo = user_pinning_repo()
        self.amocrm_class: type[AmoCRM] = amocrm_class
        self.partition_limit: int = amocrm_config["partition_limit"]

        self.logger = structlog.get_logger(self.__class__.__name__)
        self.request_limit = 5
        self.amocrm_rate_limiter = TokenBucketRateLimiter(max_tokens=self.request_limit, refill_rate=self.request_limit)
        self.lock = asyncio.Lock()

    async def __call__(
        self,
        user_id: int,
    ) -> None:
        filters: dict[str, Any] = dict(id=user_id)
        user: User = await self.user_repo.retrieve(filters=filters)
        if not user:
            raise UserNotFoundError

        status: UniqueStatus = await self._check_user(user)
        await self.user_pinning_repo.update_or_create(
            filters=dict(user=user), data=dict(unique_status=status)
        )

    async def _check_user(self, user: User) -> UniqueStatus:
        self.logger.info(f"Начало проверки закрепления для пользователя {user=}")
        async with await self.amocrm_class() as amocrm:
            await self.amocrm_rate_limiter.wait_and_acquire(num_tokens=2, timeout=3 * 60)
            async with self.lock:
                contacts: list[AmoContact] = await amocrm.fetch_contacts(
                    user_phone=user.phone, query_with=[AmoContactQueryWith.leads]
                )
            if len(contacts) == 0:
                self.logger.info(
                    f"Контакт не найден в AmoCRM {user.phone=}"
                    f"Статус закрепления {UserPinningStatusType.UNKNOWN=}"
                )
                return await get_unique_status(slug=UserPinningStatusType.UNKNOWN)
            elif len(contacts) == 1:
                self.logger.info(f"Найден один контакт в AmoCRM {user.phone=}")
                leads = await self._one_contact_case(contacts=contacts)
            else:
                self.logger.info(f"Найдено несколько контактов в AmoCRM {user.phone=}")
                leads = await self._some_contacts_case(contacts=contacts)

            status: UniqueStatus = await self._check_contact_leads(amocrm=amocrm, leads=leads)
            return status

    @staticmethod
    async def _one_contact_case(contacts: list[AmoContact]) -> list[int]:
        """
        Контакт единственный в AmoCRM
        """
        leads: set[int] = {lead.id for lead in contacts[0].embedded.leads}
        return list(leads)

    @staticmethod
    async def _some_contacts_case(contacts: list[AmoContact]) -> list[int]:
        """
        Несколько контактов в AmoCRM
        """
        leads = set()
        for contact in contacts:
            lead_ids = [lead.id for lead in contact.embedded.leads]
            leads.update(lead_ids)
        return list(leads)

    async def _check_contact_leads(self, amocrm: AmoCRM, leads: list[int]) -> UniqueStatus:
        """
        Проверяем каждую сделку клиента согласно Модели статусов закрепления (PinningStatus)
        """
        amo_leads = []
        async with self.lock:
            for lead_ids in partition_list(leads, self.partition_limit):
                await self.amocrm_rate_limiter.wait_and_acquire(num_tokens=5)
                leads = await amocrm.fetch_leads(lead_ids=lead_ids)
                amo_leads.extend(leads)

        self.logger.info(f"Найдено {len(amo_leads)} сделок в AmoCRM {amo_leads=}")
        for lead in amo_leads:
            status: Optional[UniqueStatus] = await self._check_lead_status(lead)
            if status and status.slug in (UserPinningStatusType.PINNED, UserPinningStatusType.PARTIALLY_PINNED):
                return status
        self.logger.info(f"Все проверки прошли, статус закрепления {UserPinningStatusType.NOT_PINNED=}")
        return await get_unique_status(slug=UserPinningStatusType.NOT_PINNED)

    async def _check_lead_status(self, lead: AmoLead) -> Optional[UniqueStatus]:
        """
        Проверяем статус сделки согласно Модели статусов закрепления (PinningStatus)
        Если статус 'Зкреплен' или 'Частично закреплен', то возвращаем его
        Статус 'Не закреплен' возвращаем, в случае прохождения всех проверок
        """
        self.logger.info(f"Проверка статуса закрепления для сделки {lead.id=}")
        lead_custom_fields: dict = {}
        if lead.custom_fields_values:
            lead_custom_fields = {field.field_id: field.values[0].value for field in lead.custom_fields_values}

        pinning_conditions: list[PinningStatus] = await self.check_pinning_repo.list(
            ordering="priority",
            prefetch_fields=["cities", "pipelines", "statuses", "unique_status"],
        )
        for condition in pinning_conditions:

            # Сделка находится в определенном городе
            cities_names = [city.name for city in condition.cities]
            lead_city = lead_custom_fields.get(self.amocrm_class.city_field_id)
            if not lead_city:
                self.logger.info(f"Для сделки {lead.id=} не найден город")
                continue
            if not (lead_city in cities_names):
                self.logger.info(f"Для сделки {lead.id=} город {lead_city=} не в {cities_names=}")
                continue

            # Сделка находится в определенной воронке
            pipelines_ids = [pipeline.id for pipeline in condition.pipelines]
            if not (lead.pipeline_id in pipelines_ids):
                self.logger.info(f"Для сделки {lead.id=} воронка {lead.pipeline_id=} не в {pipelines_ids=}")
                continue

            # Сделка находится в определенном статусе
            statuses_ids = [status.id for status in condition.statuses]
            if not (lead.status_id in statuses_ids):
                self.logger.info(f"Для сделки {lead.id=} статус {lead.status_id=} не в {statuses_ids=}")
                continue

            if condition.unique_status.slug in [UserPinningStatusType.PINNED, UserPinningStatusType.PARTIALLY_PINNED]:
                self.logger.info(f"Для сделки {lead.id=} статус закрепления {condition.unique_status.slug=}")
                return condition.unique_status

    def as_task(self, user_id: int) -> asyncio.Task:
        """
        Wrap into a task object
        """
        return asyncio.create_task(self(user_id=user_id))


class CheckPinningStatusServiceV2(BaseUserService):
    def __init__(
        self,
        user_repo: type[UserRepo],
        check_pinning_repo: type[PinningStatusRepo],
        user_pinning_repo: type[UserPinningStatusRepo],
    ):
        self.user_repo: UserRepo = user_repo()
        self.check_pinning_repo: PinningStatusRepo = check_pinning_repo()
        self.user_pinning_repo: UserPinningStatusRepo = user_pinning_repo()

        self.logger = structlog.get_logger(self.__class__.__name__)

    async def __call__(self, user_id: int) -> None:
        user: User = await self._get_user(user_id=user_id)
        self.logger.info(f"Start check pinning status for {user=}")
        status: UniqueStatus = await self._check_user(user=user)
        self.logger.info(f'Check pinning status for {user=} is {status.slug=}')
        await self.user_pinning_repo.update_or_create(
            filters=dict(user=user), data=dict(unique_status=status)
        )

    async def _get_user(self, user_id: int) -> User:
        filters: dict[str, Any] = dict(id=user_id)
        user: User = await self.user_repo.retrieve(
            filters=filters,
            prefetch_fields=[
                "bookings__project__city",
                "bookings__amocrm_status__pipeline",
            ],
        )
        if not user:
            raise UserNotFoundError
        return user

    async def _check_user(self, user: User) -> UniqueStatus:
        for booking in user.bookings:
            self.logger.info(f"Check {user=} pinning status for {booking=}")
            status: UniqueStatus | None = await self._check_booking_status(booking=booking)
            status_slug: str = status.slug if status else None
            self.logger.info(f"Check {user=} pinning status for {booking=} is {status_slug=}")
            if status and status.slug in (UserPinningStatusType.PINNED, UserPinningStatusType.PARTIALLY_PINNED):
                return status
        return await get_unique_status(slug=UserPinningStatusType.NOT_PINNED)

    async def _check_booking_status(self, booking: Booking) -> UniqueStatus | None:
        """
        Проверяем статус сделки согласно Модели статусов закрепления (PinningStatus)
        Если статус 'Зкреплен' или 'Частично закреплен', то возвращаем его.
        Статус 'Не закреплен' возвращаем, в случае прохождения всех проверок
        """
        pinning_conditions: list[PinningStatus] = await self.check_pinning_repo.list(
            ordering="priority",
            prefetch_fields=["cities", "pipelines", "statuses", "unique_status"],
        )
        for condition in pinning_conditions:

            # Сделка находится в определенном городе
            booking_city: City | None = booking.project.city if booking.project else None
            if not booking_city:
                self.logger.info(f'{booking=} city {booking_city=} not found')
                continue
            if not (booking_city in condition.cities):
                self.logger.info(f'{booking=} city {booking_city=} not in {condition.cities=}')
                continue

            # Сделка находится в определенной воронке
            booking_pipeline: AmocrmPipeline | None = booking.amocrm_status.pipeline if booking.amocrm_status else None
            if not (booking_pipeline in condition.pipelines):
                self.logger.info(f'{booking=} pipeline {booking_pipeline=} not in {condition.pipelines=}')
                continue

            # Сделка находится в определенном статусе
            if not (booking.amocrm_status in condition.statuses):
                self.logger.info(f'{booking=} status {booking.amocrm_status=} not in {condition.statuses=}')
                continue

            if condition.unique_status.slug in [UserPinningStatusType.PINNED, UserPinningStatusType.PARTIALLY_PINNED]:
                self.logger.info(f"For {booking=} and {condition=} pinning status is {condition.unique_status.slug=}")
                return condition.unique_status

    def as_task(self, user_id: int) -> asyncio.Task:
        """
        Wrap into a task object
        """
        return asyncio.create_task(self(user_id=user_id))
