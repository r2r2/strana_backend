# pylint: disable=unnecessary-comprehension,superfluous-parens
from copy import copy
from datetime import datetime, timedelta
from typing import Any, Optional, Type, Union

import structlog
from common.amocrm import AmoCRM
from common.amocrm.constants import AmoContactQueryWith, AmoLeadQueryWith
from common.amocrm.types import AmoContact, AmoLead
from common.utils import partition_list
from pytz import UTC

from ..constants import UserStatus, UserType
from ..entities import BaseUserService
from src.users.exceptions import UniqueStatusNotFoundError
from src.users.repos import (Check, CheckRepo, CheckTermRepo, IsConType,
                             User, UserRepo, UniqueStatusRepo, UniqueStatus)
from ..types import UserAgentRepo, UserORM


class CheckUniqueServiceV2(BaseUserService):
    """
    Проверка на уникальность
    """
    send_admin_email: bool = False

    def __init__(
        self,
        user_repo: Type[UserRepo],
        check_repo: Type[CheckRepo],
        check_term_repo: Type[CheckTermRepo],
        amocrm_class: Type[AmoCRM],
        agent_repo: Type[UserAgentRepo],
        unique_status_repo: Type[UniqueStatusRepo],
        amocrm_config: dict[Any, Any],
        orm_class: Optional[Type[UserORM]] = None,
        orm_config: Optional[dict[str, Any]] = None,
    ) -> None:
        self.user_repo: UserRepo = user_repo()
        self.check_repo: CheckRepo = check_repo()
        self.agent_repo: UserAgentRepo = agent_repo()
        self.check_term_repo: CheckTermRepo = check_term_repo()
        self.partition_limit: int = amocrm_config["partition_limit"]

        self.amocrm_class: Type[AmoCRM] = amocrm_class
        self.unique_status_repo: UniqueStatusRepo = unique_status_repo()

        self.orm_class: Union[Type[UserORM], None] = orm_class
        self.orm_config: Union[dict[str, Any], None] = copy(orm_config)
        if self.orm_config:
            self.orm_config.pop("generate_schemas", None)
        self.logger = structlog.get_logger(__name__)
        self.amocrm_id: Optional[int] = None

    async def __call__(
        self,
        phone: Optional[str] = None,
        user: Optional[User] = None,
        check: Optional[Check] = None,
        agent: Optional[User] = None,
        user_id: Optional[int] = None,
        check_id: Optional[int] = None,
        agent_id: Optional[int] = None,
    ) -> None:
        if not user and user_id:
            filters: dict[str, Any] = dict(id=user_id, type=UserType.CLIENT)
            user: User = await self.user_repo.retrieve(filters=filters)
        if not check:
            filters: dict[str, Any] = dict(id=check_id)
            check: Check = await self.check_repo.retrieve(filters=filters)
        if not phone:
            phone: str = user.phone

        assert all((check, phone)), "Не найден телефон или проверка (Check)"

        users_filter = dict(phone=phone, type__not=UserType.CLIENT)
        user_types = await self.user_repo.list(filters=users_filter).values_list("type", flat=True)
        if len(user_types) > 0:
            unique_status: UniqueStatus = await self._get_unique_status(slug=UserStatus.ERROR)
            data: dict[str, Any] = dict(unique_status=unique_status)
            await self.check_repo.update(check, data=data)
            return False

        is_unique: UniqueStatus = await self._check_unique(phone=phone)
        data: dict[str, Any] = dict(
            unique_status=is_unique,
            send_admin_email=self.send_admin_email,
            amocrm_id=self.amocrm_id,
        )
        await self.check_repo.update(check, data=data)

    async def _check_unique(self, phone: str) -> UniqueStatus:
        """
        Проверка Агентством
        """
        async with await self.amocrm_class() as amocrm:
            contacts: list[AmoContact] = await amocrm.fetch_contacts(
                user_phone=phone, query_with=[AmoContactQueryWith.leads]
            )
            if len(contacts) == 0:
                return await self._get_unique_status(slug=UserStatus.UNIQUE)
            elif len(contacts) == 1:
                leads = await self._one_contact_case(contacts=contacts)
            else:
                leads = await self._some_contacts_case(contacts=contacts)
            is_unique: UniqueStatus = await self._check_contact_leads(amocrm=amocrm, leads=leads)
        return is_unique

    @staticmethod
    async def _one_contact_case(contacts: list[AmoContact]) -> list[int]:
        """
        Контакт единственный в AmoCRM
        """
        leads: list[int] = [lead.id for lead in contacts[0].embedded.leads]
        return leads

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
        Проверяем каждую сделку клиента на уникальность
        Если хотя бы одна сделка не уникальна - пропускаем все сделки, возвращаем False
        """
        is_unique: UniqueStatus = await self._get_unique_status(slug=UserStatus.UNIQUE)

        amo_leads = []
        for amo_lead_ids in partition_list(leads, self.partition_limit):
            amo_leads.extend(await amocrm.fetch_leads(lead_ids=amo_lead_ids, query_with=[AmoLeadQueryWith.contacts]))

        for lead in amo_leads:
            is_unique: UniqueStatus = await self._check_lead_status(lead)
            if is_unique.slug in [UserStatus.NOT_UNIQUE, UserStatus.CAN_DISPUTE]:
                return is_unique
        return is_unique

    async def _check_lead_status(self, lead: AmoLead) -> UniqueStatus:
        """
        Проверка сделки на уникальность
        Запись term - проверка
        Колонка term - условие
        Если условие в проверки не прошло, то пропускаем всю проверку
        """
        lead_custom_fields: dict = {}
        if lead.custom_fields_values:
            lead_custom_fields = {field.field_id: field.values[0].value for field in lead.custom_fields_values}

        self.amocrm_id: int = lead.id

        async for term in self.check_term_repo.list(
            ordering="priority",
            prefetch_fields=["cities", "pipelines", "statuses", "unique_status"]
        ):
            # Сделка находится в определенном городе
            cities_names = [city.name for city in term.cities]
            lead_city = lead_custom_fields.get(self.amocrm_class.city_field_id)
            if not lead_city:
                continue
            if not (lead_city in cities_names):
                continue

            # Сделка находится в определенной воронке
            pipelines_ids = [pipeline.id for pipeline in term.pipelines]
            if not (lead.pipeline_id in pipelines_ids):
                continue

            # Сделка находится в определенном статусе
            statuses_ids = [status.id for status in term.statuses]
            if not (lead.status_id in statuses_ids):
                continue

            # У сделки есть или нету агента
            if term.is_agent != IsConType.SKIP:
                has_agent = await self._check_lead_has_agent(lead=lead)
                if not ((term.is_agent == IsConType.YES and has_agent) or
                        (term.is_agent == IsConType.NO and not has_agent)):
                    continue

            status_from_timestamp: Optional[int] = lead_custom_fields.get(
                self.amocrm_class.status_from_datetime_field_id)
            # Сделка находится в статусе больше дней, чем в условии
            if term.more_days and status_from_timestamp:
                gap_timestamp: int = int((datetime.now(tz=UTC) - timedelta(days=term.more_days)).timestamp())
                if not (status_from_timestamp <= gap_timestamp):
                    continue

            # Сделка находится в статусе меньше дней, чем в условии
            if term.less_days and status_from_timestamp:
                gap_timestamp: int = int((datetime.now(tz=UTC) - timedelta(days=term.more_days)).timestamp())
                if not (status_from_timestamp > gap_timestamp):
                    continue

            # Сделка находилась в статусе 'Фиксация за АН'
            if term.is_assign_agency_status != IsConType.SKIP:
                assign_agency_status = lead_custom_fields.get(self.amocrm_class.assign_agency_status_field_id, False)
                if not ((term.is_assign_agency_status == IsConType.YES and assign_agency_status) or
                        (term.is_assign_agency_status == IsConType.NO and not assign_agency_status)):
                    continue

            if term.send_admin_email:
                self.send_admin_email: bool = True
            # Если дошла до статуса - возвращаем результат
            return term.unique_status
        return await self._get_unique_status(slug=UserStatus.UNIQUE)

    async def _check_lead_has_agent(self, lead: AmoLead) -> bool:
        """
        Есть ли агент у сделки. Смотрим наличие тега "Риелтор" у контактов сделки
        """
        contacts_ids = [contact.id for contact in lead.embedded.contacts]

        async with await self.amocrm_class() as amocrm:
            contacts: list[AmoContact] = await amocrm.fetch_contacts(user_ids=contacts_ids)
        return any(
            self.amocrm_class.realtor_tag_id == tag.id
            for contact in contacts
            for tag in contact.embedded.tags
        )

    async def _get_unique_status(self, slug: str) -> UniqueStatus:
        """
        Получаем статус закрепления по slug
        """
        status: UniqueStatus = await self.unique_status_repo.retrieve(filters=dict(slug=slug))
        if not status:
            raise UniqueStatusNotFoundError
        return status
