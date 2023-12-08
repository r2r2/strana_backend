# pylint: disable=unnecessary-comprehension
from copy import copy
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Callable, Optional, Type, Union

from common.amocrm import AmoCRM
from common.amocrm.constants import AmoContactQueryWith, BaseLeadSalesStatuses
from common.amocrm.types import AmoContact, AmoCustomField, AmoLead
from common.utils import partition_list
from pytz import UTC

from ..constants import UserStatus, UserType
from ..entities import BaseUserService
from ..repos import Check, CheckRepo, User, UserRepo, CheckHistoryRepo
from ..types import UserAgentRepo, UserORM


class CheckUniqueService(BaseUserService):
    """
    [Deprecated] Проверка на уникальность
    """

    def __init__(
        self,
        user_repo: Type[UserRepo],
        check_repo: Type[CheckRepo],
        history_check_repo: Type[CheckHistoryRepo],
        amocrm_class: Type[AmoCRM],
        agent_repo: Type[UserAgentRepo],
        amocrm_config: dict[Any, Any],
        orm_class: Optional[Type[UserORM]] = None,
        orm_config: Optional[dict[str, Any]] = None,
    ) -> None:
        self.user_repo: UserRepo = user_repo()
        self.check_repo: CheckRepo = check_repo()
        self.agent_repo: UserAgentRepo = agent_repo()
        self.history_check_repo: CheckHistoryRepo = history_check_repo()
        self.partition_limit: int = amocrm_config["partition_limit"]

        self.amocrm_class: Type[AmoCRM] = amocrm_class

        self.orm_class: Union[Type[UserORM], None] = orm_class
        self.orm_config: Union[dict[str, Any], None] = copy(orm_config)
        if self.orm_config:
            self.orm_config.pop("generate_schemas", None)

    async def __call__(
        self,
        phone: Optional[str] = None,
        user: Optional[User] = None,
        check: Optional[Check] = None,
        agent: Optional[User] = None,
        user_id: Optional[int] = None,
        check_id: Optional[int] = None,
        agent_id: Optional[int] = None,
        agency_id: Optional[int] = None,
    ) -> bool:
        if not user and user_id:
            filters: dict[str, Any] = dict(id=user_id, type=UserType.CLIENT)
            user: User = await self.user_repo.retrieve(filters=filters)
        if not check:
            filters: dict[str, Any] = dict(id=check_id)
            check: Check = await self.check_repo.retrieve(filters=filters)
        if not phone:
            phone: str = user.phone

        assert all((check, phone)), "Не найден телефон или проверка (Check)"

        agent_filter: dict = dict(id=agent_id)
        agent: User = await self.agent_repo.retrieve(filters=agent_filter)
        history_check_data: dict = dict(
            status=check.status.value,
            client_id=user.id,
            agent_id=agent_id,
            agency_id=agent.agency_id,
        )
        await self.history_check_repo.create(data=history_check_data)

        users_filter = dict(phone=phone, type__not=UserType.CLIENT)
        user_types = await self.user_repo.list(filters=users_filter).values_list("type", flat=True)
        if len(user_types) > 0:
            data: dict[str, Any] = dict(status=UserStatus.ERROR)
            await self.check_repo.update(check, data=data)
            return False

        is_unique = await self._check_unique(phone=phone)

        if is_unique:
            data: dict[str, Any] = dict(status=UserStatus.UNIQUE)
            await self.check_repo.update(check, data=data)
        else:
            data: dict[str, Any] = dict(status=UserStatus.NOT_UNIQUE)
            await self.check_repo.update(check, data=data)
        return is_unique

    async def _check_unique(self, phone: str) -> bool:
        """
        Проверка Агентством
        """
        async with await self.amocrm_class() as amocrm:
            contacts: list[AmoContact] = await amocrm.fetch_contacts(
                user_phone=phone, query_with=[AmoContactQueryWith.leads]
            )
            if len(contacts) == 0:
                return True
            elif len(contacts) == 1:
                _, leads = await self._one_contact_case(contacts=contacts)
            else:
                _, leads = await self._some_contacts_case(contacts=contacts)
            is_unique: bool = await self._check_contact_leads(amocrm=amocrm, leads=leads)
        return is_unique

    @staticmethod
    async def _one_contact_case(contacts: list[AmoContact]) -> tuple[int, list[int]]:
        """
        Контакт единственный в AmoCRM
        """
        amocrm_id: int = contacts[0].id
        leads: list[int] = [lead.id for lead in contacts[0].embedded.leads]
        return amocrm_id, leads

    @staticmethod
    async def _some_contacts_case(contacts: list[AmoContact]) -> tuple[int, list[int]]:
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
        amocrm_ids = list(
            {
                amocrm_id: contact_data
                for amocrm_id, contact_data in contacts_leads_mapping.items()
            }.keys()
        )
        leads = []
        for amocrm_id in amocrm_ids:
            leads += contacts_leads_mapping[amocrm_id].get('leads', [])
        return amocrm_ids[0], leads

    async def _check_contact_leads(self, amocrm: AmoCRM, leads: list[int]) -> bool:
        """check contact leads"""
        suits: list[bool] = []

        amo_leads = []
        for amo_lead_ids in partition_list(leads, self.partition_limit):
            amo_leads.extend(await amocrm.fetch_leads(lead_ids=amo_lead_ids))
        for lead in amo_leads:
            suits.append(self._check_lead_status(lead))
        return all(suits)

    def _check_lead_status(self, lead: AmoLead) -> bool:
        """check lead status"""
        if lead.status_id in (
                self.amocrm_class.realized_status_id,
                self.amocrm_class.unrealized_status_id
        ):
            lead_close_timestamp: int = lead.closed_at or float('inf')
            return self._closed_lead_case(lead_close_timestamp)

        pipline_id: Optional[int] = lead.pipeline_id
        if pipline_id not in self.amocrm_class.sales_pipeline_ids:
            return False
        case = self._case_router(pipline_id)
        return case(lead.status_id, lead=lead)

    @staticmethod
    def _closed_lead_case(lead_update_timestamp: int) -> bool:
        """Check for realized or unrealized leads"""

        gap_timestamp: int = int((datetime.now(tz=UTC) - timedelta(days=15)).timestamp())
        return lead_update_timestamp < gap_timestamp

    def _case_router(self, pipline_id: int) -> Callable:
        """case router"""

        pipline_callable_map = {
            self.amocrm_class.PipelineIds.MOSCOW: self._sales_moscow_case,
            self.amocrm_class.PipelineIds.SPB: self._sales_spb_case,
            self.amocrm_class.PipelineIds.TYUMEN: self._sales_tyumen_case,
            self.amocrm_class.PipelineIds.EKB: self._sales_ekb_case,
            self.amocrm_class.PipelineIds.CALL_CENTER: self._sales_call_center_case,
            self.amocrm_class.PipelineIds.TEST: self._sales_test_case,
        }
        return pipline_callable_map.get(pipline_id, lambda x, *a, **k: False)

    def _sales_tyumen_case(self, status: int, *, lead: AmoLead) -> bool:
        amo_statuses = self.amocrm_class.TMNStatuses
        first_step = self.__check_sales_substage_status(status=status, amo_statuses=amo_statuses)
        return first_step and not self.__check_lead_has_agent(lead)

    def _sales_moscow_case(self, status: int, *, lead: AmoLead) -> bool:
        amo_statuses = self.amocrm_class.MSKStatuses
        first_step = self.__check_sales_substage_status(status=status, amo_statuses=amo_statuses)
        return first_step and not self.__check_lead_has_agent(lead)

    def _sales_spb_case(self, status: int, *, lead: AmoLead) -> bool:
        amo_statuses = self.amocrm_class.SPBStatuses
        first_step = self.__check_sales_substage_status(status=status, amo_statuses=amo_statuses)
        return first_step and not self.__check_lead_has_agent(lead)

    def _sales_ekb_case(self, status: int, *, lead: AmoLead) -> bool:
        amo_statuses = self.amocrm_class.EKBStatuses
        first_step = self.__check_sales_substage_status(status=status, amo_statuses=amo_statuses)
        return first_step and not self.__check_lead_has_agent(lead)

    def _sales_test_case(self, status: int, *, lead: AmoLead) -> bool:
        amo_statuses = self.amocrm_class.TestStatuses
        first_step = self.__check_sales_substage_status(status=status, amo_statuses=amo_statuses)
        return first_step and not self.__check_lead_has_agent(lead)

    def _sales_call_center_case(self, status: int, *, lead: AmoLead) -> bool:
        first_step = self._call_center_substage_case(status=status)
        return first_step and not self.__check_lead_has_agent(lead)

    def __check_lead_has_agent(self, lead: AmoLead) -> bool:
        """
        check_lead_has_agent
        """
        for field in lead.custom_fields_values:
            field: AmoCustomField
            if field.field_id == self.amocrm_class.agent_field_id:
                return True
        return False

    @staticmethod
    def __check_sales_substage_status(
            status: int,
            amo_statuses: Union[Type[BaseLeadSalesStatuses], Enum] # а вот тут после замены на IntEnum и StrEnum могу твозникнуть проблемы
    ) -> bool:
        """
        check_sales_substage_status
        """
        return status in (
            amo_statuses.START,
            amo_statuses.ASSIGN_AGENT,
            amo_statuses.MAKE_APPOINTMENT,
            amo_statuses.MEETING_IN_PROGRESS,
            amo_statuses.MAKE_DECISION,
            amo_statuses.RE_MEETING,
        )

    def _call_center_substage_case(self, status: int) -> bool:
        """Check for call-center or unrealized leads."""
        return status in (
            self.amocrm_class.CallCenterStatuses.START,
            self.amocrm_class.CallCenterStatuses.REDIAL,
            self.amocrm_class.CallCenterStatuses.ROBOT_CHECK,
            self.amocrm_class.CallCenterStatuses.TRY_CONTACT,
            self.amocrm_class.CallCenterStatuses.QUALITY_CONTROL
        )
