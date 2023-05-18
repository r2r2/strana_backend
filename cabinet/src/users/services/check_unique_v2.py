# pylint: disable=unnecessary-comprehension,superfluous-parens
from copy import copy
from datetime import datetime, timedelta
from typing import Any, Optional, Type, Union

import structlog
from common.amocrm import AmoCRM
from common.amocrm.constants import AmoContactQueryWith
from common.amocrm.types import AmoContact, AmoLead
from pytz import UTC

from ..constants import UserStatus, UserType
from ..entities import BaseUserService
from ..repos import (Check, CheckRepo, CheckTermRepo, IsConType,
                     UniqueValueType, User, UserRepo)
from ..types import UserAgentRepo, UserORM


class CheckUniqueServiceV2(BaseUserService):
    """
    Проверка на уникальность
    """
    unique_value_ratio = {
        UniqueValueType.UNIQUE: UserStatus.UNIQUE,
        UniqueValueType.NOT_UNIQUE: UserStatus.NOT_UNIQUE,
        UniqueValueType.CAN_DISPUTE: UserStatus.CAN_DISPUTE,
        UserStatus.ERROR: UserStatus.ERROR,
    }

    def __init__(
        self,
        user_repo: Type[UserRepo],
        check_repo: Type[CheckRepo],
        check_term_repo: Type[CheckTermRepo],
        amocrm_class: Type[AmoCRM],
        agent_repo: Type[UserAgentRepo],
        orm_class: Optional[Type[UserORM]] = None,
        orm_config: Optional[dict[str, Any]] = None,
    ) -> None:
        self.user_repo: UserRepo = user_repo()
        self.check_repo: CheckRepo = check_repo()
        self.agent_repo: UserAgentRepo = agent_repo()
        self.check_term_repo: CheckTermRepo = check_term_repo()

        self.amocrm_class: Type[AmoCRM] = amocrm_class

        self.orm_class: Union[Type[UserORM], None] = orm_class
        self.orm_config: Union[dict[str, Any], None] = copy(orm_config)
        if self.orm_config:
            self.orm_config.pop("generate_schemas", None)
        self.logger = structlog.get_logger(__name__)

    async def __call__(
        self,
        phone: Optional[str] = None,
        user: Optional[User] = None,
        check: Optional[Check] = None,
        agent: Optional[User] = None,
        user_id: Optional[int] = None,
        check_id: Optional[int] = None,
        agent_id: Optional[int] = None,
    ):
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
            data: dict[str, Any] = dict(status=UserStatus.ERROR)
            await self.check_repo.update(check, data=data)
            return False

        is_unique = await self._check_unique(phone=phone)
        data: dict[str, Any] = dict(status=self.unique_value_ratio[is_unique])
        await self.check_repo.update(check, data=data)

    async def _check_unique(self, phone: str) -> UserStatus:
        """
        Проверка Агентством
        """
        async with await self.amocrm_class() as amocrm:
            contacts: list[AmoContact] = await amocrm.fetch_contacts(
                user_phone=phone, query_with=[AmoContactQueryWith.leads]
            )
            if len(contacts) == 0:
                return UserStatus.UNIQUE
            elif len(contacts) == 1:
                leads = await self._one_contact_case(contacts=contacts)
            else:
                leads = await self._some_contacts_case(contacts=contacts)
            is_unique: UserStatus = await self._check_contact_leads(amocrm=amocrm, leads=leads)
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
        contacts_leads_mapping: dict[int, Any] = {}
        for contact in contacts:
            contact_id: int = contact.id
            contact_created: int = contact.created_at
            contact_updated: int = contact.updated_at
            lead_ids: list[int] = [lead.id for lead in contact.embedded.leads]
            if not lead_ids:
                continue
            contacts_leads_mapping[contact_id]: dict[str, Any] = dict(
                leads=lead_ids, created=contact_created, updated=contact_updated
            )
        # Последний созданный аккаунт
        amocrm_ids = list(contacts_leads_mapping.keys())
        leads = []
        for amocrm_id in amocrm_ids:
            leads += contacts_leads_mapping[amocrm_id].get('leads', [])
        return leads

    async def _check_contact_leads(self, amocrm: AmoCRM, leads: list[int]) -> UserStatus:
        """
        Проверяем каждую сделку клиента на уникальность
        Если хотя бы одна сделка не уникальна - пропускаем все сделки, возвращаем False
        """
        is_unique: UserStatus = UserStatus.UNIQUE
        for lead_id in leads:
            lead: Optional[AmoLead] = await amocrm.fetch_lead(lead_id=lead_id)
            if not lead:
                continue
            is_unique: UserStatus = await self._check_lead_status(lead)
            if is_unique in [UserStatus.NOT_UNIQUE, UserStatus.CAN_DISPUTE]:
                return is_unique
        return is_unique

    async def _check_lead_status(self, lead: AmoLead) -> UserStatus:
        """
        Проверка сделки на уникальность
        Запись term - проверка
        Колонка term - условие
        Если условие в проверки не прошло, то пропускаем всю проверку
        """
        self.logger.info(f"Lead: {lead.id}")
        lead_custom_fields: dict = {}
        if lead.custom_fields_values:
            lead_custom_fields = {field.field_id: field.values[0].value for field in lead.custom_fields_values}

        is_unique: UserStatus = UserStatus.UNIQUE
        async for term in self.check_term_repo.list(ordering="priority",
                                                    prefetch_fields=["cities", "pipelines", "statuses"]):
            self.logger.info(f"Current term: {term.uid}")

            # Сделка находится в определенном городе
            cities_names = [city.name for city in term.cities]
            lead_city = lead_custom_fields.get(self.amocrm_class.city_field_id)
            if not lead_city:
                continue
            if not (lead_city in cities_names):
                self.logger.info(f"Not city: lead_city={lead_city}, cities={cities_names}")
                continue

            # Сделка находится в определенной воронке
            pipelines_ids = [pipeline.id for pipeline in term.pipelines]
            if not (lead.pipeline_id in pipelines_ids):
                self.logger.info("Not pipeline")
                continue

            # Сделка находится в определенном статусе
            statuses_ids = [status.id for status in term.statuses]
            if not (lead.status_id in statuses_ids):
                self.logger.info("Not status")
                continue

            # У сделки есть или нету агента
            if term.is_agent != IsConType.SKIP:
                has_agent = self._check_lead_has_agent(lead_custom_fields)
                if not ((term.is_agent == IsConType.YES and has_agent) or
                        (term.is_agent == IsConType.NO and not has_agent)):
                    self.logger.info("Not agent")
                    continue

            status_from_timestamp: Optional[int] = lead_custom_fields.get(
                self.amocrm_class.status_from_datetime_field_id)
            # Сделка находится в статусе больше дней, чем в условии
            if term.more_days and status_from_timestamp:
                gap_timestamp: int = int((datetime.now(tz=UTC) - timedelta(days=term.more_days)).timestamp())
                if not (status_from_timestamp <= gap_timestamp):
                    self.logger.info("Not status time more")
                    continue

            # Сделка находится в статусе меньше дней, чем в условии
            if term.less_days and status_from_timestamp:
                gap_timestamp: int = int((datetime.now(tz=UTC) - timedelta(days=term.more_days)).timestamp())
                if not (status_from_timestamp > gap_timestamp):
                    self.logger.info("Not status time less")
                    continue

            # Сделка находилась в статусе 'Фиксация за АН'
            if term.is_assign_agency_status != IsConType.SKIP:
                assign_agency_status = lead_custom_fields.get(self.amocrm_class.assign_agency_status_field_id, False)
                if not ((term.is_assign_agency_status == IsConType.YES and assign_agency_status) or
                        (term.is_assign_agency_status == IsConType.NO and not assign_agency_status)):
                    self.logger.info("Not status agent assign")
                    continue

            # Если дошла до статуса - возвращаем результат
            self.logger.info(f"Terminated user check term: {term.uid}")
            return term.unique_value.value
        self.logger.info("User check term by default is unique")
        return is_unique

    def _check_lead_has_agent(self, lead_custom_fields: dict[int, Any]) -> bool:
        """
        Есть ли агент у сделки
        """
        if lead_custom_fields.get(self.amocrm_class.agent_field_id):
            return True
        return False
