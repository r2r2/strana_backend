# pylint: disable=arguments-differ
from copy import copy
from typing import Any, Optional, Type, Union

from common.amocrm import AmoCRM
from common.amocrm.constants import AmoContactQueryWith, AmoLeadQueryWith
from common.amocrm.types import AmoContact, AmoLead
from common.amocrm.types.lead import AmoLeadContact

from ..entities import BaseUserService
from ..repos import User, UserRepo
from ..types import UserAgentRepo, UserORM


class ChangeAgentService(BaseUserService):
    """
    Смена агента в AmoCRM
    """

    def __init__(
        self,
        booking_substages: Any,
        user_repo: Type[UserRepo],
        amocrm_class: Type[AmoCRM],
        agent_repo: Type[UserAgentRepo],
        orm_class: Optional[Type[UserORM]] = None,
        orm_config: Optional[dict[str, Any]] = None,
    ) -> None:
        self.user_repo: UserRepo = user_repo()
        self.agent_repo: UserAgentRepo = agent_repo()

        self.booking_substages: Any = booking_substages
        self.amocrm_class: Type[AmoCRM] = amocrm_class

        self.orm_class: Union[Type[UserORM], None] = orm_class
        self.orm_config: Union[dict[str, Any], None] = copy(orm_config)
        if self.orm_config:
            self.orm_config.pop("generate_schemas", None)

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
                tmn_substages: dict[int, str] = dict(
                    (value, key) for key, value in amocrm.tmn_status_ids.items()
                )
                msk_substages: dict[int, str] = dict(
                    (value, key) for key, value in amocrm.msk_status_ids.items()
                )
                spb_substages: dict[int, str] = dict(
                    (value, key) for key, value in amocrm.spb_status_ids.items()
                )
                ekb_substages: dict[int, str] = dict(
                    (value, key) for key, value in amocrm.ekb_status_ids.items()
                )
                test_case_substages: dict[int, str] = dict(
                    (value, key) for key, value in amocrm.test_case_status_ids.items()
                )

                contact: Optional[AmoContact] = await amocrm.fetch_contact(
                    user_id=user.amocrm_id, query_with=[AmoContactQueryWith.leads]
                )
                leads_ids: list[int] = [lead.id for lead in contact.embedded.leads]
                for lead_id in leads_ids:
                    broker_id: Optional[int] = None
                    broker_list_idx: Optional[int] = None
                    lead: Optional[AmoLead] = await amocrm.fetch_lead(
                        lead_id=lead_id,
                        query_with=[AmoLeadQueryWith.contacts],
                    )
                    if not lead:
                        continue
                    amocrm_substage: Optional[str] = None
                    if lead.status_id in amocrm.tmn_import_status_ids:
                        amocrm_substage: str = tmn_substages.get(lead.status_id)
                    elif lead.status_id in amocrm.msk_import_status_ids:
                        amocrm_substage: str = msk_substages.get(lead.status_id)
                    elif lead.status_id in amocrm.spb_import_status_ids:
                        amocrm_substage: str = spb_substages.get(lead.status_id)
                    elif lead.status_id in amocrm.ekb_import_status_ids:
                        amocrm_substage: str = ekb_substages.get(lead.status_id)
                    elif lead.status_id in amocrm.test_case_status_ids:
                        amocrm_substage: str = test_case_substages.get(lead.status_id)
                    if amocrm_substage is None or amocrm_substage in (
                            self.booking_substages.REALIZED,
                            self.booking_substages.UNREALIZED):
                        continue
                    for idx, contact in enumerate(lead.embedded.contacts):
                        contact: AmoLeadContact
                        if not contact.is_main and not broker_id:
                            fetched_contact: Optional[AmoContact] = await amocrm.fetch_contact(
                                user_id=contact.id
                            )
                            tags: list[str] = [tag.name for tag in fetched_contact.embedded.tags]
                            if amocrm.broker_tag in tags:
                                broker_id: int = contact.id
                                broker_list_idx: int = idx
                    if broker_id is not None and broker_list_idx is not None:
                        lead.embedded.contacts[broker_list_idx] = agent.amocrm_id
                        await amocrm.update_lead(
                            lead_id=lead_id,
                            contacts=[contact.id for contact in lead.embedded.contacts],
                            company=agent.agency.amocrm_id
                        )
