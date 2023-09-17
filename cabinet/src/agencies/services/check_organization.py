from copy import copy
from datetime import datetime
from typing import Any, Optional, Type, Union

from common.amocrm.constants import AmoCompanyQueryWith
from common.amocrm.types import AmoCompany
from pytz import timezone
from src.agencies.repos import Agency
from src.booking.loggers.wrappers import booking_changes_logger
from src.users.loggers.wrappers import user_changes_logger
from src.users.repos import User

from ..entities import BaseAgencyService
from ..loggers.wrappers import agency_changes_logger
from ..repos import AgencyRepo
from ..types import (AgencyAgentRepo, AgencyAmoCRM, AgencyBooking,
                     AgencyBookingRepo, AgencyCheck, AgencyCheckRepo,
                     AgencyORM, AgencyRedis)


class CheckOrganizationService(BaseAgencyService):
    """
    Создание организации в AmoCRM
    """

    def __init__(
        self,
        user_types: Any,
        redis: AgencyRedis,
        redis_config: dict[str, Any],
        agency_repo: Type[AgencyRepo],
        amocrm_class: Type[AgencyAmoCRM],
        agent_repo: Type[AgencyAgentRepo],
        check_repo: Type[AgencyCheckRepo],
        booking_repo: Type[AgencyBookingRepo],
        orm_class: Optional[Type[AgencyORM]] = None,
        orm_config: Optional[dict[str, Any]] = None,
    ) -> None:
        self.agency_repo: AgencyRepo = agency_repo()
        self.agency_update = agency_changes_logger(
            self.agency_repo.update, self, content="Обновление данных агентства"
        )
        self.agent_repo: AgencyAgentRepo = agent_repo()
        self.agent_update = user_changes_logger(
            self.agent_repo.update, self, content="Пометка агента удаленным"
        )
        self.check_repo: AgencyCheckRepo = check_repo()
        self.booking_repo: AgencyBookingRepo = booking_repo()

        self.redis: AgencyRedis = redis
        self.amocrm_class: Type[AgencyAmoCRM] = amocrm_class
        self.deleted_users_key: str = redis_config["deleted_users_key"]

        self.user_types: Any = user_types
        self.orm_class: Union[Type[AgencyORM], None] = orm_class
        self.orm_config: Union[dict[str, Any], None] = copy(orm_config)
        if self.orm_config:
            self.orm_config.pop("generate_schemas", None)

        self.booking_update = booking_changes_logger(
            self.booking_repo.update, self, content="Создание организации",
        )

        self.agency_additional_fields: dict = {
            self.amocrm_class.state_registration_number_field_id: "state_registration_number",
            self.amocrm_class.legal_address_field_id: "legal_address",
            self.amocrm_class.bank_name_field_id: "bank_name",
            self.amocrm_class.bank_identification_code_field_id: "bank_identification_code",
            self.amocrm_class.checking_account_field_id: "checking_account",
            self.amocrm_class.correspondent_account_field_id: "correspondent_account",
            self.amocrm_class.signatory_name_field_id: "signatory_name",
            self.amocrm_class.signatory_surname_field_id: "signatory_surname",
            self.amocrm_class.signatory_patronymic_field_id: "signatory_patronymic",
            self.amocrm_class.signatory_registry_number_field_id: "signatory_registry_number",
        }

    async def __call__(self) -> None:
        filters: dict[str, Any] = dict(type=self.user_types.AGENT, is_active=True, is_approved=True)
        agents_qs: Any = self.agent_repo.list(filters=filters)
        filters: dict[str, Any] = dict(
            is_deleted=False, is_approved=True, is_imported=True, amocrm_id__isnull=False
        )
        prefetch_fields: list[dict[str, Any]] = [
            dict(relation="users", queryset=agents_qs, to_attr="agents")
        ]
        deleted_agents: list[int] = []
        async with await self.amocrm_class() as amocrm:
            async for agency in self.agency_repo.list(
                filters=filters, prefetch_fields=prefetch_fields
            ):
                company: Optional[AmoCompany] = await amocrm.fetch_company(
                    agency_id=agency.amocrm_id,
                    query_with=[AmoCompanyQueryWith.contacts],
                )
                if company:
                    await self._update_agency(company)
                    contacts: list[int] = [contact.id for contact in company.embedded.contacts]
                    for agent in agency.agents:
                        if agent.amocrm_id and agent.amocrm_id not in contacts:
                            if not agent.is_deleted:
                                pass
                                #deleted_agents.append(await self._delete_agent(agent))

        if deleted_agents:
            await self.redis.connect()
            await self.redis.append(self.deleted_users_key, deleted_agents)
            await self.redis.disconnect()

    async def _delete_agent(self, agent: User) -> int:
        """
        Удаление данных агента
        """
        data: dict[str, Any] = dict(is_deleted=True)
        await self.agent_update(agent, data=data)
        filters: dict[str, Any] = dict(agent_id=agent.id)
        checks: list[AgencyCheck] = await self.check_repo.list(filters=filters)
        for check in checks:
            data: dict[str, Any] = dict(agent_id=None)
            if not check.agency_id:
                await self.check_repo.delete(check)
            else:
                await self.check_repo.update(check, data=data)
        filters: dict[str, Any] = dict(agent_id=agent.id)
        bookings: list[AgencyBooking] = await self.booking_repo.list(
            filters=filters
        )
        data: dict[str, Any] = dict(agent_id=None)
        for booking in bookings:
            await self.booking_update(booking=booking, data=data)
        return agent.id

    def _parse_custom_fields(self, amo_agency: AmoCompany) -> dict[str, Any]:
        """parse_custom_fields"""
        data = {}
        for custom_field in amo_agency.custom_fields_values:
            if custom_field.field_id in self.agency_additional_fields:
                data[self.agency_additional_fields[custom_field.field_id]] = custom_field.values[0].value
            if custom_field.field_id == self.amocrm_class.signatory_sign_date_field_id:
                data["signatory_sign_date"] = datetime.fromtimestamp(custom_field.values[0].value,
                                                                     tz=timezone("Etc/GMT-5"))

        return data

    async def _update_agency(self, company: AmoCompany):
        filters: dict[str, Any] = dict(amocrm_id=company.id)
        agency: Agency = await self.agency_repo.retrieve(filters=filters)
        additional_fields = self._parse_custom_fields(company)
        if agency and additional_fields:
            await self.agency_update(agency=agency, data=additional_fields)
