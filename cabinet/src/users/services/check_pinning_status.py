import asyncio
from typing import Any

import structlog

from common.amocrm import AmoCRM
from common.amocrm.constants import AmoContactQueryWith
from common.amocrm.types import AmoContact, AmoLead
from common.utils import partition_list
from src.users.constants import UserPinningStatusType
from src.users.entities import BaseUserService
from src.users.exceptions import UserNotFoundError
from src.users.repos import UserRepo, PinningStatusRepo, UserPinningStatusRepo, User, PinningStatus


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

        self.logger = structlog.get_logger(__name__)

    async def __call__(self, user_id: int) -> None:
        filters: dict[str, Any] = dict(id=user_id)
        user: User = await self.user_repo.retrieve(filters=filters)
        if not user:
            raise UserNotFoundError

        status: str = await self._check_user(user)
        await self.user_pinning_repo.update_or_create(
            filters=dict(user=user), data=dict(status=status)
        )

    async def _check_user(self, user: User) -> str:
        async with await self.amocrm_class() as amocrm:
            contacts: list[AmoContact] = await amocrm.fetch_contacts(
                user_phone=user.phone, query_with=[AmoContactQueryWith.leads]
            )
            if len(contacts) == 0:
                return UserPinningStatusType.UNKNOWN
            elif len(contacts) == 1:
                leads = await self._one_contact_case(contacts=contacts)
            else:
                leads = await self._some_contacts_case(contacts=contacts)

            status: str = await self._check_contact_leads(amocrm=amocrm, leads=leads)
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

    async def _check_contact_leads(self, amocrm: AmoCRM, leads: list[int]) -> str:
        """
        Проверяем каждую сделку клиента согласно Модели статусов закрепления (PinningStatus)
        """
        amo_leads = []
        for lead_ids in partition_list(leads, self.partition_limit):
            amo_leads.extend(await amocrm.fetch_leads(lead_ids=lead_ids))

        for lead in amo_leads:
            status: str = await self._check_lead_status(lead)
            if status in [UserPinningStatusType.PINNED, UserPinningStatusType.PARTIALLY_PINNED]:
                return status

        return UserPinningStatusType.NOT_PINNED

    async def _check_lead_status(self, lead: AmoLead) -> str:
        """
        Проверяем статус сделки согласно Модели статусов закрепления (PinningStatus)
        Если статус 'Зкреплен' или 'Частично закреплен', то возвращаем его
        Статус 'Не закреплен' возвращаем, в случае прохождения всех проверок
        """
        self.logger.info(f"Lead: {lead.id}")
        lead_custom_fields: dict = {}
        if lead.custom_fields_values:
            lead_custom_fields = {field.field_id: field.values[0].value for field in lead.custom_fields_values}

        pinning_conditions: list[PinningStatus] = await self.check_pinning_repo.list(
            ordering="priority",
            prefetch_fields=["cities", "pipelines", "statuses"],
        )
        for condition in pinning_conditions:
            self.logger.info(f"Condition: {condition.id}")

            # Сделка находится в определенном городе
            cities_names = [city.name for city in condition.cities]
            lead_city = lead_custom_fields.get(self.amocrm_class.city_field_id)
            if not lead_city:
                continue
            if not (lead_city in cities_names):
                self.logger.info(f"Not city: lead_city={lead_city}, cities={cities_names}")
                continue

            # Сделка находится в определенной воронке
            pipelines_ids = [pipeline.id for pipeline in condition.pipelines]
            if not (lead.pipeline_id in pipelines_ids):
                self.logger.info("Not pipeline")
                continue

            # Сделка находится в определенном статусе
            statuses_ids = [status.id for status in condition.statuses]
            if not (lead.status_id in statuses_ids):
                self.logger.info("Not status")
                continue

            if condition.result.value in [UserPinningStatusType.PINNED, UserPinningStatusType.PARTIALLY_PINNED]:
                self.logger.info(f"Terminated user check condition: {condition.id}")
                return condition.result.value

        self.logger.info("Все проверки прошли - пользователь не закреплен")
        return UserPinningStatusType.NOT_PINNED

    def as_task(self, user_id: int) -> asyncio.Task:
        """
        Wrap into a task object
        """
        return asyncio.create_task(self(user_id=user_id))
