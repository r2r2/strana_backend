import asyncio
import random
from typing import Any, Optional

import structlog

from common.amocrm import AmoCRM
from common.amocrm.constants import AmoContactQueryWith
from common.amocrm.types import AmoContact, AmoLead
from common.redis import Redis, broker as redis
from common.unleash.client import UnleashClient
from common.utils import partition_list
from config.feature_flags import FeatureFlags
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
        lead_id: int | None = None,
    ) -> None:
        filters: dict[str, Any] = dict(id=user_id)
        user: User = await self.user_repo.retrieve(filters=filters)
        if not user:
            raise UserNotFoundError

        status: UniqueStatus = await self._check_user(user, lead_id)
        await self.user_pinning_repo.update_or_create(
            filters=dict(user=user), data=dict(unique_status=status)
        )

    async def _check_user(self, user: User, lead_id: int | None = None) -> UniqueStatus:
        async with await self.amocrm_class() as amocrm:
            await self.amocrm_rate_limiter.wait_and_acquire(num_tokens=2, timeout=3 * 60)
            async with self.lock:
                contacts: list[AmoContact] = await amocrm.fetch_contacts(
                    user_phone=user.phone, query_with=[AmoContactQueryWith.leads]
                )
            if len(contacts) == 0:
                return await get_unique_status(slug=UserPinningStatusType.UNKNOWN)
            elif len(contacts) == 1:
                leads = await self._one_contact_case(contacts=contacts)
            else:
                leads = await self._some_contacts_case(contacts=contacts)

            if lead_id and self.__is_strana_lk_3183_enable:
                leads = [lead_id]

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

        for lead in amo_leads:
            status: Optional[UniqueStatus] = await self._check_lead_status(lead)
            if status and status.slug in (UserPinningStatusType.PINNED, UserPinningStatusType.PARTIALLY_PINNED):
                return status

        return await get_unique_status(slug=UserPinningStatusType.NOT_PINNED)

    async def _check_lead_status(self, lead: AmoLead) -> Optional[UniqueStatus]:
        """
        Проверяем статус сделки согласно Модели статусов закрепления (PinningStatus)
        Если статус 'Зкреплен' или 'Частично закреплен', то возвращаем его
        Статус 'Не закреплен' возвращаем, в случае прохождения всех проверок
        """
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
                continue
            if not (lead_city in cities_names):
                continue

            # Сделка находится в определенной воронке
            pipelines_ids = [pipeline.id for pipeline in condition.pipelines]
            if not (lead.pipeline_id in pipelines_ids):
                continue

            # Сделка находится в определенном статусе
            statuses_ids = [status.id for status in condition.statuses]
            if not (lead.status_id in statuses_ids):
                continue

            if condition.unique_status.slug in [UserPinningStatusType.PINNED, UserPinningStatusType.PARTIALLY_PINNED]:
                return condition.unique_status

    def as_task(self, user_id: int) -> asyncio.Task:
        """
        Wrap into a task object
        """
        return asyncio.create_task(self(user_id=user_id))

    @property
    def __is_strana_lk_3183_enable(self) -> bool:
        return UnleashClient().is_enabled(FeatureFlags.strana_lk_3183)
