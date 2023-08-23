# pylint: disable=arguments-differ

from copy import copy
from typing import Any, Optional, Type, Union

from common.amocrm import AmoCRM
from common.amocrm.constants import AmoContactQueryWith, AmoLeadQueryWith
from common.amocrm.types import AmoContact, AmoLead
from common.utils import partition_list

from ..constants import UserStatus, UserType
from ..entities import BaseUserService
from ..loggers.wrappers import user_changes_logger
from ..repos import Check, CheckRepo, User, UserRepo, UniqueStatus
from ..types import UserAgentRepo, UserORM
from src.users.utils import get_unique_status


class CheckClientService(BaseUserService):
    """
    Проверка клиента в AmoCRM
    """

    def __init__(
        self,
        booking_substages: Any,
        user_repo: Type[UserRepo],
        check_repo: Type[CheckRepo],
        amocrm_class: Type[AmoCRM],
        agent_repo: Type[UserAgentRepo],
        amocrm_config: dict[Any, Any],
        orm_class: Optional[Type[UserORM]] = None,
        orm_config: Optional[dict[str, Any]] = None,
    ) -> None:
        self.user_repo: UserRepo = user_repo()
        self.user_update = user_changes_logger(
            self.user_repo.update, self, content="Проверка клиента в AmoCRM | Обновление агента и агентства"
        )
        self.check_repo: CheckRepo = check_repo()
        self.agent_repo: UserAgentRepo = agent_repo()
        self.partition_limit: int = amocrm_config["partition_limit"]

        self.booking_substages: Any = booking_substages
        self.amocrm_class: Type[AmoCRM] = amocrm_class

        self.orm_class: Union[Type[UserORM], None] = orm_class
        self.orm_config: Union[dict[str, Any], None] = copy(orm_config)
        if self.orm_config:
            self.orm_config.pop("generate_schemas", None)

    async def __call__(self) -> None:
        amocrm: AmoCRM
        async with await self.amocrm_class() as amocrm:
            filters: dict[str, Any] = dict(
                agent_id__isnull=False,
                agency_id__isnull=False,
                amocrm_id__isnull=False,
                type=UserType.CLIENT,
            )
            async for user in self.user_repo.list(
                filters=filters, related_fields=["agency", "agent"]
            ):
                unique_status: UniqueStatus = await get_unique_status(slug=UserStatus.UNIQUE)
                filters: dict[str, Any] = dict(user_id=user.id, unique_status=unique_status)
                check: Check = await self.check_repo.retrieve(filters=filters)
                if not check:
                    continue
                broker_id: Optional[int] = None
                contact: Optional[AmoContact] = await amocrm.fetch_contact(
                    user_id=user.amocrm_id, query_with=[AmoContactQueryWith.leads]
                )
                if not contact:
                    await self.user_update(user=user, data=dict(is_deleted=True))
                    continue

                leads_ids: list[int] = [lead.id for lead in contact.embedded.leads]
                amo_leads = []
                for amo_lead_ids in partition_list(leads_ids, self.partition_limit):
                    amo_leads.extend(
                        await amocrm.fetch_leads(lead_ids=amo_lead_ids, query_with=[AmoLeadQueryWith.contacts])
                    )

                for lead in amo_leads:
                    amocrm_substage: Optional[str] = None
                    if lead.status_id in amocrm.tmn_import_status_ids:
                        amocrm_substage: str = amocrm.tmn_substages.get(lead.status_id)
                    elif lead.status_id in amocrm.msk_import_status_ids:
                        amocrm_substage: str = amocrm.msk_substages.get(lead.status_id)
                    elif lead.status_id in amocrm.spb_import_status_ids:
                        amocrm_substage: str = amocrm.spb_substages.get(lead.status_id)
                    elif lead.status_id in amocrm.ekb_import_status_ids:
                        amocrm_substage: str = amocrm.ekb_substages.get(lead.status_id)
                    elif lead.status_id in amocrm.test_case_status_ids:
                        amocrm_substage: str = amocrm.test_case_substages.get(lead.status_id)
                    if amocrm_substage is None or amocrm_substage in (self.booking_substages.REALIZED,
                                                                      self.booking_substages.UNREALIZED):
                        continue
                    lead_contacts: list[int] = [contact.id for contact in lead.embedded.contacts]
                    if lead_contacts and user.agent.amocrm_id not in lead_contacts:
                        for _, lead_contact in enumerate(lead_contacts):
                            if lead_contact != user.amocrm_id and not broker_id:
                                fetched_contact: Optional[AmoContact] = await amocrm.fetch_contact(
                                    user_id=lead_contact
                                )
                                tags: list[str] = [tag.name for tag in fetched_contact.embedded.tags]
                                if amocrm.broker_tag in tags:
                                    broker_id: int = lead_contact
                if broker_id is not None:
                    filters: dict[str, Any] = dict(
                        is_active=True,
                        is_deleted=False,
                        is_approved=True,
                        amocrm_id=broker_id,
                        type=UserType.AGENT,
                    )
                    agent: User = await self.agent_repo.retrieve(
                        filters=filters, related_fields=["agency"]
                    )
                    if agent:
                        data: dict[str, Any] = dict(agent_id=agent.id, agency_id=agent.agency_id)
                        await self.user_update(user=user, data=data)
                        await self.check_repo.update(check, data=data)
            await self.set_amocrm_id_to_users_without_it(amocrm=amocrm)

    async def set_amocrm_id_to_users_without_it(self, amocrm: AmoCRM) -> None:
        """
        Заполняет поле amocrm_id у пользователей, у которых оно пустое.
        """
        users: list[User] = await self.get_users_without_amocrm_id()
        for user in users:
            contacts: list[AmoContact] = await amocrm.fetch_contacts(
                user_phone=user.phone,
            )
            if not contacts:
                continue
            if len(contacts) == 1:
                amocrm_id = contacts[0].id
            else:
                amocrm_id = await self._some_contacts_case(contacts=contacts)
            data: dict[str, int] = dict(amocrm_id=amocrm_id)
            await self.user_update(user=user, data=data)

    async def get_users_without_amocrm_id(self) -> list[User]:
        """
        Возвращает список пользователей, у которых поле amocrm_id пустое.
        """
        filters: dict[str, Any] = dict(
            amocrm_id__isnull=True,
            type=UserType.CLIENT,
        )
        users: list[User] = await self.user_repo.list(filters=filters)
        return users

    async def _some_contacts_case(self, contacts: list[AmoContact]) -> int:
        """
        Несколько контактов в AmoCRM
        """
        contacts_leads_mapping: dict[int, Any] = {}
        for contact in contacts:
            contact_id: int = contact.id
            contact_created: int = contact.created_at
            contact_updated: int = contact.updated_at
            lead_ids: list[int] = [lead.id for lead in contact.embedded.leads]
            contacts_leads_mapping[contact_id]: dict[str, Any] = dict(
                leads=lead_ids, created=contact_created, updated=contact_updated
            )
        # Последний созданный аккаунт
        latest_amocrm_id: int = list(
            {
                amocrm_id: contact_data
                for amocrm_id, contact_data in contacts_leads_mapping.items()
                if contact_data["created"]
                == max(lead_item["created"] for _, lead_item in contacts_leads_mapping.items())
            }.keys()
        )[0]
        return latest_amocrm_id
