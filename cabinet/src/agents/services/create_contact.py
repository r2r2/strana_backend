from copy import copy
from typing import Any, Optional, Type, Union
from pydantic import parse_obj_as

from common.amocrm.types import AmoContact, AmoTag
from ..entities import BaseAgentService
from ..exceptions import AgentNotFoundError
from ..repos import AgentRepo, User
from ..types import AgentAgency, AgentAgencyRepo, AgentAmoCRM, AgentORM
from src.users.loggers.wrappers import user_changes_logger


class CreateContactService(BaseAgentService):
    """
    Создание контакта в AmoCRM
    """

    lk_broker_tag: list[str] = ["ЛК Брокера"]

    def __init__(
        self,
        agent_repo: Type[AgentRepo],
        amocrm_class: Type[AgentAmoCRM],
        agency_repo: Type[AgentAgencyRepo],
        orm_class: Optional[Type[AgentORM]] = None,
        orm_config: Optional[dict[str, Any]] = None,
    ) -> None:
        self.agent_repo: AgentRepo = agent_repo()
        self.agent_update = user_changes_logger(
            self.agent_repo.update, self, content="Обновление агента из AmoCRM"
        )
        self.agency_repo: AgentAgencyRepo = agency_repo()

        self.amocrm_class: Type[AgentAmoCRM] = amocrm_class

        self.orm_class: Union[Type[AgentORM], None] = orm_class
        self.orm_config: Union[dict[str, Any], None] = copy(orm_config)
        if self.orm_config:
            self.orm_config.pop("generate_schemas", None)

    async def __call__(
        self,
        phone: Optional[str] = None,
        agent: Optional[User] = None,
        agent_id: Optional[int] = None,
    ) -> tuple[int, list[Any]]:
        agent: User = agent or await self.agent_repo.retrieve(filters=dict(id=agent_id))
        if not agent:
            raise AgentNotFoundError
        if not phone:
            phone: str = agent.phone
        filters: dict[str, Any] = dict(id=agent.agency_id)
        agency: AgentAgency = await self.agency_repo.retrieve(filters=filters)
        async with await self.amocrm_class() as amocrm:
            contacts: list[AmoContact] = await amocrm.fetch_contacts(user_phone=phone)
            amocrm_id, tags = await self._contact_case_router(amocrm=amocrm, phone=phone, contacts=contacts)
            amocrm_id, tags = await self._update_contact_data(
                amocrm=amocrm,
                user_tags=tags,
                user_id=amocrm_id,
                user_name=agent.name,
                user_email=agent.email,
                user_surname=agent.surname,
                user_patronymic=agent.patronymic,
                user_company=agency.amocrm_id,
            )
        data: dict[str, Any] = dict(amocrm_id=amocrm_id, tags=tags, is_imported=True)
        await self.agent_update(agent, data=data)
        return amocrm_id, tags

    async def _contact_case_router(
            self, amocrm: AgentAmoCRM, phone: str, contacts: list[AmoContact]
    ) -> tuple[int, list[AmoTag]]:
        """
        contact case router
        """
        if len(contacts) == 0:
            return await self._no_contacts_case(amocrm=amocrm, phone=phone)
        elif len(contacts) == 1:
            return await self._one_contact_case(contacts=contacts)
        return await self._some_contacts_case(contacts=contacts)

    async def _no_contacts_case(self, amocrm: AgentAmoCRM, phone: str) -> tuple[int, list[AmoTag]]:
        """
        Контакт не существует в AmoCRM
        """
        contact: list[Any] = await amocrm.create_contact(user_phone=phone, tags=self.lk_broker_tag)
        amocrm_id: int = contact[0]["id"]
        tags: list[AmoTag] = parse_obj_as(list[AmoTag], contact[0].get("tags", []))
        return amocrm_id, tags

    async def _one_contact_case(self, contacts: list[AmoContact]) -> tuple[int, list[AmoTag]]:
        """
        Контакт единственный в AmoCRM
        """
        amocrm_id: int = contacts[0].id
        tags: list[AmoTag] = contacts[0].embedded.tags
        return amocrm_id, tags

    async def _some_contacts_case(self, contacts: list[AmoContact]) -> tuple[int, list[AmoTag]]:
        """
        Несколько контактов в AmoCRM
        """
        contacts_mapping: dict[int, tuple[int, int, list[AmoTag]]] = {}
        for contact in contacts:
            contact_id: int = contact.id
            contact_tags: list[AmoTag] = contact.embedded.tags
            contact_created: int = contact.created_at
            contacts_mapping[contact_id] = (contact_created, contact_id, contact_tags)
        _, amocrm_id, tags = contacts_mapping[max(contacts_mapping, key=contacts_mapping.get)]
        return amocrm_id, tags

    async def _update_contact_data(
        self,
        user_id: int,
        user_name: str,
        user_email: str,
        user_surname: str,
        user_patronymic: str,
        user_company: int,
        user_tags: list[AmoTag],
        amocrm: AgentAmoCRM,
    ) -> tuple[int, list[str]]:
        """
        Обновление данных контакта
        todo: Дубликат с CreateContactService для represes
        """
        if amocrm.broker_tag not in [tag.name for tag in user_tags]:
            user_tags.append(AmoTag(name=amocrm.broker_tag))
        update_options: dict[str, Any] = dict(
            user_id=user_id,
            user_tags=[tag.dict(exclude_none=True) for tag in user_tags],
            user_email=user_email,
            user_company=user_company,
            user_name=f"{user_surname} {user_name} {user_patronymic}",
        )
        await amocrm.update_contact(**update_options)
        return user_id, [tag.name for tag in user_tags]
