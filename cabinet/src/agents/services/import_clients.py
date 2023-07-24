"""
Import clients
"""
from asyncio import Task
from copy import copy
from datetime import datetime
from typing import Any, AsyncGenerator, List, Optional, Set, Tuple, Type, Union
from enum import Enum

import structlog
from common.amocrm.constants import AmoContactQueryWith, AmoLeadQueryWith
from common.amocrm.types import AmoContact, AmoCustomField, AmoLead
from common.amocrm.repos import AmoStatusesRepo
from common.email import EmailService
from common.utils import parse_phone, partition_list
from pydantic import BaseModel
from pytz import UTC
from src.users.constants import UserType
from src.users.loggers.wrappers import user_changes_logger
from src.notifications.services import GetEmailTemplateService

from ...booking.constants import BookingSubstages
from ...booking.loggers import booking_changes_logger
from ...booking.repos import Booking, BookingRepo
from ..entities import BaseAgentService
from ..exceptions import AgentNotFoundError
from ..repos import AgentRepo, User
from ..types import (AgentAmoCRM, AgentCheck, AgentCheckRepo, AgentORM,
                     AgentUserRepo)


class LeadStatuses(int, Enum):
    """
     Статусы закрытых сделок в амо.
    """
    REALIZED: int = 142  # Успешно реализовано
    UNREALIZED: int = 143  # Закрыто и не реализовано


class RequestDataDto(BaseModel):
    agent_id: int
    client_id: int


class ImportClientsService(BaseAgentService):
    """
    Импорт клиентов из AmoCRM
    """

    mail_event_slug = 'agent_unassign_client'

    def __init__(
        self,
        user_statuses: Any,
        booking_substages: Any,
        import_bookings_task: Any,
        agent_repo: Type[AgentRepo],
        booking_repo: Type[BookingRepo],
        amocrm_class: Type[AgentAmoCRM],
        user_repo: Type[AgentUserRepo],
        check_repo: Type[AgentCheckRepo],
        email_class: Type[EmailService],
        amocrm_config: dict[Any, Any],
        statuses_repo: Type[AmoStatusesRepo],
        get_email_template_service: GetEmailTemplateService,
        logger: Optional[Any] = structlog.getLogger(__name__),
        orm_class: Optional[Type[AgentORM]] = None,
        orm_config: Optional[dict[str, Any]] = None,
    ) -> None:
        self.agent_repo: AgentRepo = agent_repo()
        self.booking_repo: BookingRepo = booking_repo()
        self.agent_update_amocrm_id = user_changes_logger(
            self.agent_repo.update, self, content="Обновление amocrm_id агента из AmoCRM"
        )
        self.user_repo: AgentUserRepo = user_repo()
        self.client_update = user_changes_logger(
            self.user_repo.update, self, content="Обновление клиента из AmoCRM"
        )
        self.client_exist_update = user_changes_logger(
            self.user_repo.update, self, content="Обновление существующего клиента из AmoCRM"
        )
        self.user_create = user_changes_logger(
            self.user_repo.create, self, content="Создание клиента из AmoCRM"
        )
        self.unbind_client = user_changes_logger(
            self.user_repo.update, self, content="Импорт клиентов из AmoCRM | Отвязка клиента от агента"
        )
        self.check_repo: AgentCheckRepo = check_repo()
        self.booking_repo: BookingRepo = booking_repo()
        self.email_class = email_class

        self.user_statuses: Any = user_statuses
        self.booking_substages: Any = booking_substages
        self.amocrm_class: Type[AgentAmoCRM] = amocrm_class
        self.import_bookings_task: Any = import_bookings_task
        self.statuses_repo: AmoStatusesRepo = statuses_repo()
        self.get_email_template_service: GetEmailTemplateService = get_email_template_service

        self.orm_class: Union[Type[AgentORM], None] = orm_class
        self.orm_config: Union[dict[str, Any], None] = copy(orm_config)
        if self.orm_config:
            self.orm_config.pop("generate_schemas", None)
        self.partition_limit: int = amocrm_config["partition_limit"]

        self.logger = logger

    async def __call__(self, agent: Optional[User] = None, agent_id: Optional[int] = None):
        agent: User = agent or await self.agent_repo.retrieve(filters=dict(id=agent_id), related_fields=["agency"])
        if not agent:
            raise AgentNotFoundError
        if not agent.amocrm_id:
            self.logger.warning(f"Agent has no amocrm_id: id={agent.id}")
            return
        client_ids: set = set()

        async with await self.amocrm_class() as amocrm:
            agent_contact = await amocrm.fetch_contact(user_id=agent.amocrm_id, query_with=[AmoContactQueryWith.leads])

            if not agent_contact:
                self.logger.warning(f"Agent has no amo contact: amocrm_id={agent.amocrm_id}")
                return

            agent_contact_id = agent_contact.id

            leads_gen: AsyncGenerator = self._fetch_leads(amocrm, agent_contact)

            async for leads in leads_gen:
                self.logger.info(f"Fetched leads: {[lead.id for lead in leads]}")
                for lead in leads:
                    client_ids.update(self._client_ids_by_lead(amocrm, lead, agent_contact_id))
            self.logger.info(f"Agent '{agent_id}' has {len(client_ids)} clients")

        await self._unbind_clients(agent, client_ids)
        if not client_ids:
            return

        filters: dict[str, Any] = dict(amocrm_id__in=client_ids, type=UserType.CLIENT)
        users: List[User] = await self.user_repo.list(filters=filters, prefetch_fields=["agent"])
        self.logger.info(f"Users agents: {[user.agent for user in users]}")
        user_map: dict[int, User] = {user.amocrm_id: user for user in users}
        self.logger.info(f"User map: {user_map}")
        async with await self.amocrm_class() as amocrm:
            contacts: list[AmoContact] = await amocrm.fetch_contacts(user_ids=client_ids)
        contacts_map: dict[int, AmoContact] = {contact.id: contact for contact in contacts}

        self.logger.info(f"client_ids '{client_ids}'")
        self.logger.info(f"user_map '{user_map}'")
        for client_amocrm_id in client_ids:
            user = user_map.get(client_amocrm_id)
            self.logger.info(f"Users '{user}' if true create else update")
            if not user:
                user = await self._fetch_client_from_amo(contacts_map, client_amocrm_id, agent)
            else:
                old_agent = user.agent
                await self._update_existing_client_data(agent=agent, user=user)
                if old_agent and old_agent.id != agent.id:
                    await self._proceed_changed_assign(client=user, agent=old_agent)

            if user:
                self.import_bookings_task.delay(user_id=user.id)

    async def _fetch_leads(self, amocrm_context, agent_contact) -> AsyncGenerator:
        """fetch_leads"""
        big_lead_ids: list[int] = [lead.id for lead in agent_contact.embedded.leads]
        for lead_ids in partition_list(big_lead_ids, self.partition_limit):
            yield await amocrm_context.fetch_leads(lead_ids=lead_ids, query_with=[AmoLeadQueryWith.contacts])

    def _client_ids_by_lead(self, amocrm_context, lead: AmoLead, contact_id: int) -> Set:
        """client_ids_by_lead"""
        client_ids = set()
        amocrm_substage = self._substage_by_lead(amocrm_context, lead)

        if amocrm_substage in (self.booking_substages.REALIZED, self.booking_substages.UNREALIZED):
            return client_ids

        for contact in lead.embedded.contacts:
            if contact.id != contact_id:
                client_ids.add(contact.id)
        return client_ids

    @staticmethod
    def _substage_by_lead(amocrm_context, lead: AmoLead) -> Optional[str]:
        """substage_by_lead"""
        amocrm_substage = ""
        if lead.status_id in amocrm_context.tmn_import_status_ids:
            amocrm_substage: str = amocrm_context.tmn_substages.get(lead.status_id)
        elif lead.status_id in amocrm_context.msk_import_status_ids:
            amocrm_substage: str = amocrm_context.msk_substages.get(lead.status_id)
        elif lead.status_id in amocrm_context.spb_import_status_ids:
            amocrm_substage: str = amocrm_context.spb_substages.get(lead.status_id)
        elif lead.status_id in amocrm_context.ekb_import_status_ids:
            amocrm_substage: str = amocrm_context.ekb_substages.get(lead.status_id)
        elif lead.status_id in amocrm_context.test_import_status_ids:
            amocrm_substage: str = amocrm_context.test_case_substages.get(lead.status_id)
        return amocrm_substage

    async def _fetch_client_from_amo(self, contacts_map, client_amocrm_id, agent) -> Optional[User]:
        """
        Получает из амо и создает/обновляет клиента
        """
        contact: AmoContact = contacts_map.get(client_amocrm_id)
        name, surname, patronymic = self._get_personal_names(contact)
        phone, email = self._get_custom_fields(contact)
        if not phone:
            return
        self.logger.info(f"Start load data for client with amo_id, phone, email: {client_amocrm_id}, {phone}, {email}")

        return await self._proceed_client_data_storage(agent, client_amocrm_id, name, surname, patronymic, phone, email)

    @staticmethod
    def _get_personal_names(contact) -> Tuple[str, Optional[str], Optional[str]]:
        """get_personal_names"""
        name_components: List[str] = contact.name.split()
        name = surname = patronymic = None
        if len(name_components) == 1:
            name = name_components[0]
        elif len(name_components) == 2:
            surname, name = name_components
        else:
            surname, name, patronymic = name_components
        return name, surname, patronymic

    def _get_custom_fields(self, contact) -> Tuple[Optional[str], Optional[str]]:
        """get_custom_fields"""
        parsed_phone: Optional[str] = None
        email: Optional[str] = None

        custom_fields: list[AmoCustomField] = contact.custom_fields_values
        for custom_field in custom_fields:
            if custom_field.field_id == self.amocrm_class.phone_field_id:
                phone: Optional[str] = custom_field.values[0].value
                self.logger.info(f"Base phone: {phone}")
                if phone:
                    parsed_phone: Optional[str] = parse_phone(phone)
                    if not parsed_phone:
                        self.logger.warning(f"Amo send incorrect phone format: {phone}")
                        return (None, None)

            elif custom_field.field_id == self.amocrm_class.email_field_id:
                email: Optional[str] = custom_field.values[0].value
                if len(email) < 5:
                    email = None
        return parsed_phone, email

    async def _proceed_client_data_storage(
            self,
            agent: User,
            client_amocrm_id: int,
            name: str,
            surname: Optional[str],
            patronymic: Optional[str],
            phone: Optional[str],
            email: Optional[str]
    ) -> Optional[User]:
        """
        Логика создания/обновления клиента в БД
        """
        client: Optional[User] = None
        if phone or email:
            q_filters = [
                self.user_repo.q_builder(or_filters=[dict(phone=phone), dict(email__iexact=email)])
            ]
            filters = dict(type=UserType.CLIENT)
            client: User = await self.user_repo.retrieve(filters=filters, q_filters=q_filters)

        if client:
            self.logger.info(f"Client with amo_id found (id: '{client.id}'). Updating data")
            data: dict[str, Any] = dict(amocrm_id=client_amocrm_id)
            return await self.client_update(client, data)

        if not phone and not email:
            self.logger.warning(f"Client with amo_id '{client_amocrm_id}' has no both phone and email")
            return

        self.logger.info(f"Client with amo_id '{client_amocrm_id}' was not found. Start creation")
        data: dict[str, Any] = dict(
            name=name,
            email=email,
            phone=phone,
            surname=surname,
            agent_id=agent.id,
            patronymic=patronymic,
            agency_id=agent.agency_id,
            amocrm_id=client_amocrm_id,
            is_brokers_client=True,
            is_active=True,
            is_approved=True,
            type=UserType.CLIENT,
        )
        user: User = await self.user_create(data=data)
        data: dict[str, Any] = dict(
            user_id=user.id,
            agent_id=agent.id,
            agency_id=agent.agency_id,
            requested=datetime.now(tz=UTC),
            status=self.user_statuses.UNIQUE,
        )
        await self.check_repo.create(data=data)
        return user

    async def _update_existing_client_data(self, agent: User, user: User):
        """update_existing_client_data"""
        self.logger.info(f"Start updating data for client with id '{user.id}'")

        data: dict[str, Any] = dict(
            agent_id=agent.id,
            agency_id=agent.agency_id,
            is_active=True,
            is_approved=True,
            type=UserType.CLIENT,
        )
        user: User = await self.client_exist_update(user, data=data)
        filters: dict[str, Any] = dict(agent_id=agent.id)
        check: AgentCheck = await self.check_repo.retrieve(filters=filters, ordering='-id')
        if check:
            data: dict[str, Any] = dict(agent_id=agent.id, agency_id=agent.agency_id)
            await self.check_repo.update(check, data=data)
        else:
            data: dict[str, Any] = dict(
                user_id=user.id,
                agent_id=agent.id,
                agency_id=agent.agency_id,
                requested=datetime.now(tz=UTC),
                status=self.user_statuses.UNIQUE,
            )
            await self.check_repo.create(data=data)

    async def _send_agent_email(self, recipients: list[str], **context) -> Task:
        """
        Отправляем уведомление агенту о том что клиент отказался от закрепления.
        @param recipients: list[str]
        @param context: Any (Контекст, который будет использоваться в шаблоне письма)
        @return: Task
        """
        email_notification_template = await self.get_email_template_service(
            mail_event_slug=self.mail_event_slug,
            context=context,
        )

        if email_notification_template and email_notification_template.is_active:
            email_options: dict[str, Any] = dict(
                topic=email_notification_template.template_topic,
                content=email_notification_template.content,
                recipients=recipients,
                lk_type=email_notification_template.lk_type.value,
                mail_event_slug=email_notification_template.mail_event_slug,
            )
            email_service: EmailService = self.email_class(**email_options)
            return email_service.as_task()

    async def _proceed_changed_assign(self, client: User, agent: User):
        """change assign"""
        await self._update_amocrm_leads(client=client)
        client_agent_dto = RequestDataDto(
            client_id=client.id,
            agent_id=agent.id
        )
        await self._update_booking_data(user_data=client_agent_dto)
        await self._send_agent_email(
            recipients=[agent.email],
            client_name=client.full_name
        )

    async def _update_booking_data(self, user_data: RequestDataDto) -> None:
        """
        Отвязывание всех сделок клиента от агента.
        Ставим статус ЗАКРЫТО и НЕ РЕАЛИЗОВАНО, active=False.
        """
        filters = dict(user_id=user_data.client_id, agent_id=user_data.agent_id, active=True)
        data: dict[str, Any] = dict(
            agent_id=None,
            agency_id=None,
            amocrm_stage=Booking.stages.DDU_UNREGISTERED,
            amocrm_substage=Booking.substages.UNREALIZED,
            active=False
        )
        await self.booking_repo.bulk_update(filters=filters, data=data)

    async def _update_amocrm_leads(self, client: User):
        """
        Обновить сделки пользователя в амо.
        Всем сделкам ставим статус "закрыто и не реализовано"
        @param client: User
        """
        filters: dict[str, Any] = dict(
            active=True,
            user_id=client.id,
            agent_id=client.agent_id
        )
        bookings: list[Booking] = await self.booking_repo.list(
            filters=filters, prefetch_fields=['project', 'project__city']
        )

        async with await self.amocrm_class() as amocrm:
            for booking in bookings:
                if booking.amocrm_id:
                    lead_options: dict[str, Any] = dict(
                        status=BookingSubstages.UNREALIZED,
                        lead_id=booking.amocrm_id,
                        city_slug=booking.project.city.slug,
                    )
                    await amocrm.update_lead(**lead_options)

    async def _unbind_clients(self, agent, amocrm_clients_ids: set):
        """unbind"""
        filters = dict(
            agent_id=agent.id,
            is_active=True,
        )
        lk_clients_list: List[User] = await self.user_repo.list(
            filters=filters,
            prefetch_fields=["agent"],
        )

        for client in lk_clients_list:
            if client.amocrm_id not in amocrm_clients_ids:
                await self._unbind_agent_from_bookings(agent, client)
                await self.unbind_client(client, data=dict(agent_id=None, agency_id=None))

    async def _unbind_agent_from_bookings(self, agent, client):
        """
        Открепляем агента от активных сделок клиента, делаем сделки неактивными и помечаем их как закрытые.
        """
        filters = dict(
            agent_id=agent.id,
            user_id=client.id,
            active=True,
        )
        data = dict(
            active=False,
            agent_id=None,
            amocrm_status_id=LeadStatuses.UNREALIZED,
        )

        await self.booking_repo.bulk_update(filters=filters, data=data)
