from copy import copy
from typing import Any, Optional, Type, Union

from common.amocrm.types import AmoContact, AmoTag

from ..entities import BaseRepresService
from ..repos import RepresRepo, User
from ..types import RepresAgency, RepresAgencyRepo, RepresAmoCRM, RepresORM
from src.users.loggers.wrappers import user_changes_logger


class CreateContactService(BaseRepresService):
    """
    Создание контакта в AmoCRM
    """

    lk_broker_tag: list[str] = ["ЛК Брокера"]

    def __init__(
        self,
        repres_repo: Type[RepresRepo],
        amocrm_class: Type[RepresAmoCRM],
        agency_repo: Type[RepresAgencyRepo],
        orm_class: Optional[Type[RepresORM]] = None,
        orm_config: Optional[dict[str, Any]] = None,
    ) -> None:
        self.repres_repo: RepresRepo = repres_repo()
        self.repres_update = user_changes_logger(
            self.repres_repo.update, self, content="Обновление данных представителя"
        )
        self.agency_repo: RepresAgencyRepo = agency_repo()

        self.amocrm_class: Type[RepresAmoCRM] = amocrm_class

        self.orm_class: Union[Type[RepresORM], None] = orm_class
        self.orm_config: Union[dict[str, Any], None] = copy(orm_config)
        if self.orm_config:
            self.orm_config.pop("generate_schemas", None)

    async def __call__(
        self,
        phone: Optional[str] = None,
        repres: Optional[User] = None,
        repres_id: Optional[int] = None,
    ) -> tuple[int, list[Any]]:
        if not repres:
            filters: dict[str, Any] = dict(id=repres_id)
            repres: User = await self.repres_repo.retrieve(filters=filters)
        if not phone:
            phone: str = repres.phone
        filters: dict[str, Any] = dict(
            id=repres.maintained_id if repres.maintained_id is not None else repres.agency_id
        )
        agency: RepresAgency = await self.agency_repo.retrieve(filters=filters)
        async with await self.amocrm_class() as amocrm:
            contacts: list[AmoContact] = await amocrm.fetch_contacts(user_phone=phone)
            if len(contacts) == 0:
                amocrm_id, tags = await self._no_contacts_case(amocrm=amocrm, phone=phone)
            elif len(contacts) == 1:
                amocrm_id, tags = await self._one_contact_case(contact=contacts[0])
            else:
                amocrm_id, tags = await self._some_contacts_case(contacts=contacts)
            amocrm_id, tags = await self._update_contact_data(
                amocrm=amocrm,
                user_tags=tags,
                user_id=amocrm_id,
                user_name=repres.name,
                user_email=repres.email,
                user_surname=repres.surname,
                user_patronymic=repres.patronymic,
                user_company=agency.amocrm_id,
            )
        data: dict[str, Any] = dict(amocrm_id=amocrm_id, tags=tags, is_imported=True)
        await self.repres_update(repres, data=data)
        return amocrm_id, tags

    async def _no_contacts_case(self, amocrm: RepresAmoCRM, phone: str) -> tuple[int, list[Any]]:
        """
        Контакт не существует в AmoCRM
        """
        contact: list[Any] = await amocrm.create_contact(user_phone=phone, tags=self.lk_broker_tag)

        amocrm_id: int = contact[0]["id"]
        amo_contact = await amocrm.fetch_contact(user_id=amocrm_id)
        return amocrm_id, amo_contact.embedded.tags

    async def _one_contact_case(self, contact: AmoContact) -> tuple[int, list[AmoTag]]:
        """
        Контакт единственный в AmoCRM
        """
        amocrm_id: int = contact.id
        tags: list[AmoTag] = contact.embedded.tags
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
        amocrm: RepresAmoCRM,
    ):
        """
        Обновление данных контакта
        todo: Дубликат с CreateContactService для agents
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
