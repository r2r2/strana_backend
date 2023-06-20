# pylint: disable=arguments-differ
import asyncio
from typing import Any, Optional, Type
from enum import IntEnum

from common.amocrm import AmoCRM
from common.amocrm.constants import AmoContactQueryWith, AmoLeadQueryWith, AmoCompanyEntityType
from common.amocrm.types import AmoContact, AmoLead
from common.amocrm.models import Entity
from common.utils import partition_list

from ..entities import BaseUserService
from ..repos import User, UserRepo
from ..types import UserAgentRepo, UserORM


class LeadStatuses(IntEnum):
    """
     Статусы закрытых сделок в амо.
    """
    REALIZED: int = 142  # Успешно реализовано
    UNREALIZED: int = 143  # Закрыто и не реализовано


class ChangeAgentService(BaseUserService):
    """
    Смена агента в AmoCRM
    """

    def __init__(
        self,
        user_repo: Type[UserRepo],
        amocrm_class: Type[AmoCRM],
        agent_repo: Type[UserAgentRepo],
        amocrm_config: dict[Any, Any],
    ) -> None:
        self.user_repo: UserRepo = user_repo()
        self.agent_repo: UserAgentRepo = agent_repo()
        self.amocrm_class: Type[AmoCRM] = amocrm_class

        self.partition_limit: int = amocrm_config["partition_limit"]

    async def __call__(
        self,
        user: Optional[User] = None,
        agent: Optional[User] = None,
        user_id: Optional[int] = None,
        agent_id: Optional[int] = None,
    ) -> None:
        if not user:
            filters: dict[str, Any] = dict(id=user_id)
            user: User = await self.user_repo.retrieve(filters=filters, related_fields=["agent"])
        if not agent:
            filters: dict[str, Any] = dict(id=agent_id)
            agent: User = await self.user_repo.retrieve(filters=filters, related_fields=["agency"])
        if user.amocrm_id:
            amocrm: AmoCRM
            async with await self.amocrm_class() as amocrm:
                contact: Optional[AmoContact] = await amocrm.fetch_contact(
                    user_id=user.amocrm_id, query_with=[AmoContactQueryWith.leads]
                )
                big_lead_ids: list[int] = [lead.id for lead in contact.embedded.leads]
                leads = []
                for lead_ids in partition_list(big_lead_ids, self.partition_limit):
                    leads.extend(await amocrm.fetch_leads(lead_ids=lead_ids, query_with=[AmoLeadQueryWith.contacts]))

                active_leads: list[AmoLead] = [
                    lead for lead in leads if lead.status_id not in (
                        LeadStatuses.REALIZED,
                        LeadStatuses.UNREALIZED
                    )
                ]
                active_leads_ids: list[int] = [lead.id for lead in active_leads]

                # находим старые агентства и старых агентов в активных сделках клиента в амо
                old_agents = set()
                old_companies = set()
                for lead in active_leads:
                    for contact in lead.embedded.contacts:
                        if contact.id != user.amocrm_id:
                            old_agents.add(contact.id)
                    if lead.embedded.companies:
                        old_companies.add(lead.embedded.companies[0].id)

                # формируем для всех сущностей агентов и агентств модели
                old_agent_entities: Entity = Entity(ids=old_agents, type=AmoCompanyEntityType.contacts)
                old_agency_entities: Entity = Entity(ids=old_companies, type=AmoCompanyEntityType.companies)
                agent_entities: Entity = Entity(ids=[agent.amocrm_id], type=AmoCompanyEntityType.contacts)
                agency_entities: Entity = Entity(ids=[agent.agency.amocrm_id], type=AmoCompanyEntityType.companies)

                # отвязываем старое агентство и старых агентов от всех активных сделок клиента в амо
                await amocrm.leads_unlink_entities(
                    lead_ids=active_leads_ids,
                    entities=[old_agent_entities, old_agency_entities],
                )

                # привязываем новое агентство и нового агента ко всем активным сделкам клиента в амо
                await amocrm.leads_link_entities(
                    lead_ids=active_leads_ids,
                    entities=[agent_entities, agency_entities],
                )

    def as_task(
        self,
        user: Optional[User] = None,
        agent: Optional[User] = None,
        user_id: Optional[int] = None,
        agent_id: Optional[int] = None,
    ) -> asyncio.Task:
        """
        Wrap into a task object
        """
        return asyncio.create_task(self(
            user=user,
            agent=agent,
            user_id=user_id,
            agent_id=agent_id,
        ))
