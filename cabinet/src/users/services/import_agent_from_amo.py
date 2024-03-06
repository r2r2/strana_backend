from typing import Any

import structlog

from common.amocrm import AmoCRM
from common.amocrm.constants import AmoLeadQueryWith, AmoEntityTypes
from common.amocrm.types import AmoContact, AmoLead, AmoCompany
from src.booking.types import WebhookLead
from .create_contact import CreateContactService
from ..constants import UserType, OriginType
from ..repos import UserRepo, User, UserRoleRepo, UserRole
from ...agencies.exceptions import AgentAgencyNotFoundError
from ...agencies.repos import AgencyRepo, Agency
from ...booking.repos import BookingRepo


class ImportAgentFromAmoService(CreateContactService):
    """
    Импорт данных агента из АМО
    """
    user_tag: str = "Риелтор"
    user_type: str = UserType.AGENT
    ORIGIN: str = OriginType.AMOCRM

    no_city_message = "Город агенства и агента не проставлен, нужно проставить его в АМО и в админке ЛК"

    default_city = "Тюмень"

    logger = structlog.getLogger(__name__)

    def __init__(
            self,
            user_repo: type[UserRepo],
            user_role_repo: type[UserRoleRepo],
            agencies_repo: type[AgencyRepo],
            booking_repo: type[BookingRepo],
            amocrm_class: type[AmoCRM],
    ) -> None:
        self.user_repo: UserRepo = user_repo()
        self.user_role_repo: UserRoleRepo = user_role_repo()
        self.agencies_repo: AgencyRepo = agencies_repo()
        self.booking_repo: BookingRepo = booking_repo()
        self.amocrm_class: type[AmoCRM] = amocrm_class

        self.agency_custom_fields: dict = {
            self.amocrm_class.inn_field_id: "inn",
            self.amocrm_class.agency_city: "city",
        }

    async def __call__(self, webhook_lead: WebhookLead) -> list[User] | None:
        self.logger.info(f"Start importing agent from {webhook_lead.lead_id}")
        lead_id: int = webhook_lead.lead_id
        async with await self.amocrm_class() as amocrm:
            amo_lead: AmoLead | None = await amocrm.fetch_lead(
                lead_id=lead_id, query_with=[AmoLeadQueryWith.contacts]
            )
            if not amo_lead:
                self.logger.warning("Users(EXCEPT MAIN) has not found at amo contact before fetch")
                return

            agent_amocrm_id, client_id = self._get_agents(amo_lead=amo_lead)
            contacts: list[AmoContact] = await amocrm.fetch_contacts(
                user_ids=agent_amocrm_id
            )

            filters = dict(amocrm_id=client_id)
            client = await self.user_repo.retrieve(filters=filters)

            if not contacts:
                self.logger.warning("Users(EXCEPT MAIN) has not found at amo contact after fetch")
                return

            updated_users = []
            for contact in contacts:

                if self.user_tag not in [tag.name for tag in contact.embedded.tags]:
                    continue

                data: dict = await self.fetch_amocrm_data(contact)
                user_role: UserRole = await self.user_role_repo.retrieve(
                    filters=dict(slug=self.user_type)
                )
                phone: str = data.get("phone")
                user_by_phone: User | None = await self.user_repo.retrieve(
                    filters=dict(phone=phone, role=user_role)
                )
                user_by_amocrm_id: User | None = await self.user_repo.retrieve(
                    filters=dict(amocrm_id=contact.id, role=user_role)
                )
                found_user = user_by_phone or user_by_amocrm_id

                if contact.embedded.companies:
                    filters = dict(amocrm_id=contact.embedded.companies[0].id)
                    agency: Agency = await self.agencies_repo.retrieve(filters=filters)
                    if not agency:
                        amo_agency: AmoCompany | None = await amocrm.fetch_company(
                            agency_id=contact.embedded.companies[0].id
                        )
                        if amo_agency:
                            agency_data = amo_agency.dict()
                            agency_data.update(await self._parse_custom_fields(amo_agency))
                            if not agency_data.get("city"):
                                await amocrm.create_note_v4(
                                    lead_id=contact.id,
                                    text=self.no_city_message,
                                    entity_type=AmoEntityTypes.CONTACTS
                                )
                                agency_data["city"] = self.default_city
                            agency_data["amocrm_id"] = agency_data.pop("id")
                            agency = await self.agencies_repo.create(data=agency_data)
                        else:
                            raise AgentAgencyNotFoundError
                    data.update(agency_id=agency.id)

                if found_user:
                    new_agent: User = await self.user_repo.update(
                        model=found_user, data=data
                    )
                    updated_users.append(new_agent)
                else:
                    data.update(
                        amocrm_id=contact.id,
                        type=self.user_type,
                        origin=self.ORIGIN,
                        role=user_role,
                    )
                    new_agent: User = await self.user_repo.create(data=data)
                    updated_users.append(new_agent)

            filters = dict(amocrm_id=lead_id)
            booking = await self.booking_repo.retrieve(filters=filters)
            booking_data = dict(agent_id=new_agent.id, agency_id=agency.id)
            await self.booking_repo.update(booking, data=booking_data)
            client_data = dict(agent_id=new_agent.id, agency_id=agency.id)
            await self.user_repo.update(client, data=client_data)

            self.logger.info(f"End importing agent from {webhook_lead.lead_id}")
            return updated_users

    def _get_agents(self, amo_lead: AmoLead) -> tuple[list[int], int]:
        agents = []
        if contacts := amo_lead.embedded.contacts:
            for contact in contacts:
                if not contact.is_main:
                    agents.append(contact.id)
                else:
                    client = contact.id
            return agents, client

    async def fetch_amocrm_data(self, contact: AmoContact, with_personal: bool = True) -> dict:
        """
        Fetch_amocrm_data
        """
        surname, name, patronymic = self._get_personal_names(contact)
        phone, email, passport_series, passport_number, birth_date, tags = self._get_custom_fields(contact)
        data: dict[str, Any] = dict(
            name=name,
            email=email,
            phone=phone,
            surname=surname,
            patronymic=patronymic,
            tags=tags,
        )
        if with_personal:
            personal_data = dict(
                passport_series=passport_series,
                passport_number=passport_number,
                birth_date=birth_date
            )
            data.update(personal_data)
        return data

    async def _parse_custom_fields(self, amo_agency: AmoCompany) -> dict[str, Any]:
        """parse_custom_fields"""
        data = {}
        for custom_field in amo_agency.custom_fields_values:
            if custom_field.field_id in self.agency_custom_fields.keys():
                data[self.agency_custom_fields[custom_field.field_id]] = custom_field.values[0].value
        return data
