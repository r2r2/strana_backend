"""
Import clients and all booking
"""
from asyncio import Task, create_task
from copy import copy
from datetime import datetime
from typing import Any, AsyncGenerator, List, Set, Tuple, Type, Union
from enum import IntEnum

import structlog
from common.amocrm.constants import AmoContactQueryWith, AmoLeadQueryWith
from common.amocrm.types import AmoContact, AmoCustomField, AmoLead
from common.amocrm.repos import AmoStatusesRepo
from common.email import EmailService
from common.unleash.client import UnleashClient
from common.utils import parse_phone, partition_list
from pydantic import BaseModel
from pytz import UTC

from config.feature_flags import FeatureFlags
from src.booking.loggers import booking_changes_logger
from src.users.constants import UserType
from src.users.loggers.wrappers import user_changes_logger
from src.notifications.services import GetEmailTemplateService
from src.users.repos import UserRoleRepo

from ...booking.constants import BookingSubstages
from ...booking.repos import Booking, BookingRepo
from ..entities import BaseAgentService
from ..exceptions import AgentNotFoundError
from ..repos import AgentRepo, User
from ..types import (AgentAmoCRM, AgentCheck, AgentCheckRepo, AgentORM,
                     AgentUserRepo)
from src.users.utils import get_unique_status


class LeadStatuses(IntEnum):
    """
     Статусы закрытых сделок в амо.
    """
    REALIZED: int = 142  # Успешно реализовано
    UNREALIZED: int = 143  # Закрыто и не реализовано


class RequestDataDto(BaseModel):
    agent_id: int
    client_id: int


class ImportClientsAllBookingService(BaseAgentService):
    """
    Импорт клиентов из AmoCRM со всеми сделками
    """

    mail_event_slug = 'agent_unassign_client'

    def __init__(
        self,
        user_statuses: Any,
        booking_substages: Any,
        import_bookings_task: Any,
        import_bookings_service: Any,
        agent_repo: Type[AgentRepo],
        booking_repo: Type[BookingRepo],
        amocrm_class: Type[AgentAmoCRM],
        user_repo: Type[AgentUserRepo],
        user_role_repo: type[UserRoleRepo],
        check_repo: Type[AgentCheckRepo],
        email_class: Type[EmailService],
        amocrm_config: dict[Any, Any],
        statuses_repo: Type[AmoStatusesRepo],
        get_email_template_service: GetEmailTemplateService,
        logger: Any = structlog.getLogger(__name__),
        orm_class: Type[AgentORM] | None = None,
        orm_config: dict[str, Any] | None = None,
    ) -> None:
        self.agent_repo: AgentRepo = agent_repo()
        self.booking_repo: BookingRepo = booking_repo()
        self.agent_update_amocrm_id = user_changes_logger(
            self.agent_repo.update, self, content="Обновление amocrm_id агента из AmoCRM"
        )
        self.user_repo: AgentUserRepo = user_repo()
        self.user_role_repo: UserRoleRepo = user_role_repo()
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
        self.booking_bulk_update = booking_changes_logger(
            self.booking_repo.bulk_update, self,
            content="Открепляем агента от активных сделок клиента, "
                    "делаем сделки неактивными и помечаем их как закрытые.",
        )
        self.check_repo: AgentCheckRepo = check_repo()
        self.booking_repo: BookingRepo = booking_repo()
        self.email_class = email_class

        self.user_statuses: Any = user_statuses
        self.booking_substages: Any = booking_substages
        self.amocrm_class: Type[AgentAmoCRM] = amocrm_class
        self.import_bookings_task: Any = import_bookings_task
        self.import_bookings_service: Any = import_bookings_service
        self.statuses_repo: AmoStatusesRepo = statuses_repo()
        self.get_email_template_service: GetEmailTemplateService = get_email_template_service

        self.orm_class: Union[Type[AgentORM], None] = orm_class
        self.orm_config: Union[dict[str, Any], None] = copy(orm_config)
        if self.orm_config:
            self.orm_config.pop("generate_schemas", None)
        self.partition_limit: int = amocrm_config["partition_limit"]

        self.logger = logger

    async def __call__(self, agent: User | None = None, agent_id: int | None = None) -> None:
        """
        Получаем агента и сделки с ним.
        Из сделок выбираем id клиентов
        отвязываем их
        Выбираем клиентов по amo_id из своей базы
        Выбираем чанками пользователей из АМО и создаём или обновляем их на основе нашей базы
        Импортируем таской сделки по пользователям
        """

        if self.__is_strana_lk_3412_enable():
            self.logger.debug(f"3412 ImportClientsAllBookingService called {agent=} {agent_id=}")

        agent: User = agent or await self.agent_repo.retrieve(filters=dict(id=agent_id), related_fields=["agency"])

        if not agent:
            raise AgentNotFoundError
        if not agent.amocrm_id:
            self.logger.warning(f"Agent has no amocrm_id: id={agent.id}")
            return

        amo_client_ids = await self._get_amo_client_ids(agent)


        if self.__is_strana_lk_3412_enable():
            self.logger.debug(f"3412 Контакты агента в АМО: {agent=} ({agent.amocrm_id}) {amo_client_ids=}")
            self.logger.debug(f"3412 len={len(amo_client_ids)}")

        # self.logger.info(f"Agent '{agent_id} ({agent.amocrm_id})' has {len(amo_client_ids)} clients")

        if not amo_client_ids:
            return

        await self._unbind_clients_from_old_agent(agent, amo_client_ids)

        filters: dict[str, Any] = dict(amocrm_id__in=amo_client_ids, type=UserType.CLIENT)
        users: List[User] = await self.user_repo.list(filters=filters, prefetch_fields=["agent"])

        if self.__is_strana_lk_3412_enable():
            self.logger.debug(f"3412 Клиенты агента в базе: {[user.agent for user in users]}")
            self.logger.debug(f"3412 len={len(users)}")

        cabinet_user_map: dict[int, User] = {user.amocrm_id: user for user in users}

        if self.__is_strana_lk_3412_enable():
            self.logger.debug(f"3412 Замапленные клиенты из базы  User map (amocrm_id: user): {cabinet_user_map}")
            self.logger.debug(f"3412 len={len(cabinet_user_map)}")

        async with await self.amocrm_class() as amocrm:
            amo_contacts_gen: AsyncGenerator = self._fetch_contacts_without_limit(amocrm, amo_client_ids)

            amo_contacts_map: dict[int, AmoContact] = dict()
            async for amo_contacts in amo_contacts_gen:
                for amo_contact in amo_contacts:
                    amo_contacts_map[amo_contact.id] = amo_contact

        if self.__is_strana_lk_3412_enable():
            self.logger.debug(f"3412 Замапленные контакты из АМО (amo_contact.id: amo_contact) len={len(amo_contacts_map)}")

            # self.logger.info(f"amo_client_ids '{amo_client_ids}'")
            # self.logger.info(f"user_map '{cabinet_user_map}'")

        client_for_import_booking = []

        for client_amocrm_id in amo_client_ids:
            # if client_amocrm_id != 50917068:
            #     continue
            user = cabinet_user_map.get(client_amocrm_id)
            if self.__is_strana_lk_3412_enable():
                self.logger.debug(f"3412 Users '{user}'. if true create else update")
            if not user:
                user = await self._fetch_client_from_amo(amo_contacts_map, client_amocrm_id, agent)
                self.logger.debug(f"3412 User '{user}' created")
            else:
                old_agent = user.agent
                await self._update_existing_client_data(agent=agent, user=user)
                self.logger.debug(f"3412 User '{user}' updated")
                if old_agent and old_agent.id != agent.id:
                    # Если не совпадают ЗАКРЫВАЕМ СДЕЛКИ (и в АМО тоже)
                    self.logger.info(f"3412 _proceed_changed_assign_in_amo_and_cabinet '{user}' {old_agent.id} {agent.id}")
                    await self._proceed_changed_assign_in_amo_and_cabinet(client=user, agent=old_agent)
            if user:
                if self.__is_strana_lk_3412_enable():
                    self.logger.debug(f"3412 Create task for update '{user}' {user.id} booking")
                    client_for_import_booking.append(user.id)
                # TOD
                self.import_bookings_task.delay(user_id=user.id)
                # await self.import_bookings_service(user_id=user.id)
            else:
                self.logger.error(f"3412 Пользователь с {client_amocrm_id=} не создан")

        if self.__is_strana_lk_3412_enable():
            self.logger.debug(f"3412 Пользователи для обновления сделок {client_for_import_booking=}")
            self.logger.debug(f"3412 len={len(client_for_import_booking)}")

    async def _fetch_leads(self, amocrm_context, agent_contact) -> AsyncGenerator:
        """fetch_leads"""
        big_lead_ids: list[int] = [lead.id for lead in agent_contact.embedded.leads]
        for lead_ids in partition_list(big_lead_ids, self.partition_limit):
            yield await amocrm_context.fetch_leads(lead_ids=lead_ids, query_with=[AmoLeadQueryWith.contacts])

    def _amo_client_ids_by_lead(self, lead: AmoLead, contact_id: int) -> Set:
        """
        Получаем список id клиентов из всех сделок АМО.

        Т.е. с открытыми и закрытыми сделками тоже

        """
        amo_client_ids = set()
        for contact in lead.embedded.contacts:
            if contact.id != contact_id:
                amo_client_ids.add(contact.id)
        return amo_client_ids


    @staticmethod
    def _substage_by_lead(amocrm_context, lead: AmoLead) -> str | None:
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

    async def _fetch_client_from_amo(self, amo_contacts_map, client_amocrm_id, agent) -> User | None:
        """
        Получает из амо и создает/обновляет клиента
        """
        contact: AmoContact = amo_contacts_map.get(client_amocrm_id)

        if contact is None:
            self.logger.error(f"3412 Не нашли контакт из АМО {client_amocrm_id=}")
            return None
        name, surname, patronymic = self._get_personal_names(contact)
        phone, email = self._get_custom_fields(contact)
        if not phone:
            return
        self.logger.info(f"3412 Start load data for client with amo_id, phone, email: {client_amocrm_id}, {phone}, {email}")

        return await self._proceed_client_data_storage(agent, client_amocrm_id, name, surname, patronymic, phone, email)

    @staticmethod
    def _get_personal_names(contact) -> Tuple[str, str | None, str | None]:
        """get_personal_names"""
        name_components: List[str] = contact.name.split()
        name = surname = patronymic = None
        if len(name_components) == 1:
            name = name_components[0]
        elif len(name_components) == 2:
            surname, name = name_components
        elif len(name_components) == 3:
            surname, name, patronymic = name_components
        else:
            surname, name, patronymic, *_ = name_components

        return name, surname, patronymic

    def _get_custom_fields(self, contact) -> Tuple[str | None, str | None]:
        """get_custom_fields"""
        parsed_phone: str | None = None
        email: str | None = None

        custom_fields: list[AmoCustomField] = contact.custom_fields_values
        for custom_field in custom_fields:
            if custom_field.field_id == self.amocrm_class.phone_field_id:
                phone: str | None = custom_field.values[0].value
                self.logger.info(f"Base phone: {phone}")
                if phone:
                    parsed_phone: str | None = parse_phone(phone)
                    if not parsed_phone:
                        self.logger.warning(f"Amo send incorrect phone format: {phone}")
                        return (None, None)

            elif custom_field.field_id == self.amocrm_class.email_field_id:
                email = custom_field.values[0].value
                if len(email) < 5:
                    email = None
        return parsed_phone, email

    async def _proceed_client_data_storage(
            self,
            agent: User,
            client_amocrm_id: int,
            name: str,
            surname: str | None,
            patronymic: str | None,
            phone: str | None,
            email: str | None,
    ) -> User | None:
        """
        Логика создания/обновления клиента в БД
        """
        client: User | None = None
        if phone or email:
            q_filters = [
                self.user_repo.q_builder(or_filters=[dict(phone=phone), dict(email__iexact=email)])
            ]
            filters = dict(type=UserType.CLIENT)
            client: User = await self.user_repo.retrieve(filters=filters, q_filters=q_filters)

        if client:
            self.logger.info(f"Client with amo_id found (id: '{client.id}'). Updating data")
            data: dict[str, Any] = dict(
                amocrm_id=client_amocrm_id,
                agent_id=agent.id,
                agency_id=agent.agency_id,
            )
            return await self.client_update(client, data)

        if not phone and not email:
            self.logger.warning(f"Client with amo_id '{client_amocrm_id}' has no both phone and email")
            return

        self.logger.info(f"Client with amo_id '{client_amocrm_id}' was not found. Start creation")
        user_role = await self.user_role_repo.retrieve(filters=dict(slug=UserType.CLIENT))
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
            role=user_role,
        )
        user: User = await self.user_create(data=data)
        data: dict[str, Any] = dict(
            user_id=user.id,
            agent_id=agent.id,
            agency_id=agent.agency_id,
            requested=datetime.now(tz=UTC),
            unique_status=await get_unique_status(slug=self.user_statuses.UNIQUE),
        )
        await self.check_repo.create(data=data)
        return user

    async def _update_existing_client_data(self, agent: User, user: User):
        """update_existing_client_data"""
        self.logger.info(f"3412 Start updating data for client with id '{user.id}'")

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
                unique_status=await get_unique_status(slug=self.user_statuses.UNIQUE),
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

    async def _proceed_changed_assign_in_amo_and_cabinet(self, client: User, agent: User):
        """change assign"""
        await self._update_amocrm_leads(client=client, agent=agent)
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
            amocrm_stage=Booking.stages.DDU_UNREGISTERED,
            amocrm_substage=Booking.substages.UNREALIZED,
            active=False
        )
        await self.booking_bulk_update(filters=filters, data=data)

    async def _update_amocrm_leads(self, client: User, agent: User):
        """
        Обновить сделки пользователя в амо.
        Всем сделкам ставим статус "закрыто и не реализовано"
        @param client: User
        """
        filters: dict[str, Any] = dict(
            active=True,
            user_id=client.id,
            agent_id=agent.id
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

                    if self.__is_strana_lk_3412_enable():
                        self.logger.debug(f"3412 Want to set UNREALIZED booking {booking.amocrm_id}")
                    # TOD
                    await amocrm.update_lead(**lead_options)

    async def _unbind_clients_from_old_agent(self, agent, amocrm_clients_ids: set):
        """unbind"""
        filters = dict(
            agent_id=agent.id,
            is_active=True,
        )
        lk_clients_list: List[User] = await self.user_repo.list(
            filters=filters,
            prefetch_fields=["agent"],
        )

        if self.__is_strana_lk_3412_enable():
            self.logger.debug(f"3412 _unbind_clients_from_old_agent {lk_clients_list=}")

        for client in lk_clients_list:
            if client.amocrm_id not in amocrm_clients_ids:
                await self._unbind_agent_from_bookings(agent, client)
                await self.unbind_client(client, data=dict(agent_id=None, agency_id=None))

    async def _unbind_agent_from_bookings(self, agent, client):
        """
        Открепляем агента от активных сделок клиента, делаем сделки неактивными и помечаем их как закрытые.
        """
        if self.__is_strana_lk_3412_enable():
            self.logger.debug(f"_unbind_agent_from_bookings agent_id={agent.id} client_id={client.id}")
        filters = dict(
            agent_id=agent.id,
            user_id=client.id,
            active=True,
        )
        exclude_filters: list[dict] = [
            dict(amocrm_status_id=LeadStatuses.REALIZED),
            dict(amocrm_status_id=LeadStatuses.UNREALIZED),
        ]
        data = dict(
            active=False,
            amocrm_status_id=LeadStatuses.UNREALIZED,
        )
        await self.booking_bulk_update(filters=filters, data=data, exclude_filters=exclude_filters)

    async def _get_amo_client_ids(self, agent) -> set:
        """
        Получаем id ВСЕХ клиентов агента
        """

        amo_client_ids: set = set()

        async with await self.amocrm_class() as amocrm:
            agent_contact = await amocrm.fetch_contact(user_id=agent.amocrm_id, query_with=[AmoContactQueryWith.leads])

        if not agent_contact:
            self.logger.warning(f"Agent has no amo contact: amocrm_id={agent.amocrm_id}")
            return amo_client_ids

        async with await self.amocrm_class() as amocrm:
            agent_contact = await amocrm.fetch_contact(user_id=agent.amocrm_id, query_with=[AmoContactQueryWith.leads])

            self.logger.debug(f"Agent: amocrm_id={agent.amocrm_id}")
            self.logger.debug(f"{agent_contact=}")

            if not agent_contact:
                self.logger.warning(f"Agent has no amo contact: amocrm_id={agent.amocrm_id}")
                return amo_client_ids

            agent_contact_id = agent_contact.id

            leads_gen: AsyncGenerator = self._fetch_leads(amocrm, agent_contact)

            async for leads in leads_gen:
                self.logger.info(f":Fetched leads {[lead.id for lead in leads]}")
                for lead in leads:
                    amo_client_ids.update(self._amo_client_ids_by_lead(lead, agent_contact_id))

            return amo_client_ids

    async def _fetch_contacts_without_limit(self, amocrm_context, all_amo_client_ids) -> AsyncGenerator:
        all_amo_client_ids_list = list(all_amo_client_ids)
        for amo_client_ids in partition_list(all_amo_client_ids_list, self.partition_limit):

            yield await amocrm_context.fetch_contacts(user_ids=amo_client_ids)

    def __is_strana_lk_3412_enable(self) -> bool:
        return UnleashClient().is_enabled(FeatureFlags.strana_lk_3412)
