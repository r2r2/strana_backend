# pylint: disable=missing-param-doc,missing-raises-doc,redundant-returns-doc
import asyncio
import json
from asyncio import Task
from base64 import b64encode
from datetime import datetime
from urllib.parse import unquote
from enum import IntEnum
from typing import Any, Callable, Optional, Tuple, Type, Union, Awaitable

import structlog
from pytz import UTC
from fastapi import Request

from common.amocrm import AmoCRM
from common.amocrm.constants import AmoContactQueryWith, AmoCompanyEntityType, AmoLeadQueryWith
from common.amocrm.repos import AmoStatusesRepo
from common.amocrm.types import AmoContact, AmoLead
from common.amocrm.models import Entity
from common.backend.models import AmocrmStatus
from common.email import EmailService
from common.utils import partition_list
from config import EnvTypes, maintenance_settings
from src.amocrm.repos import AmocrmGroupStatus, AmocrmPipeline
from src.agents.types import AgentEmail, AgentSms
from src.booking.constants import BookingCreatedSources, BookingStages, BookingStagesMapping, BookingSubstages
from src.booking.repos import (
    Booking,
    BookingRepo,
    BookingFixingConditionsMatrix,
    BookingFixingConditionsMatrixRepo,
    BookingSource,
)
from src.booking.loggers import booking_changes_logger
from src.booking.utils import get_booking_source, create_lead_name
from src.cities.repos import City
from src.notifications.services import GetEmailTemplateService
from src.notifications.repos import AssignClientTemplate, AssignClientTemplateRepo
from src.task_management.dto import CreateTaskDTO
from src.projects.constants import ProjectStatus
from src.task_management.services import CreateTaskInstanceService
from src.projects.repos import Project, ProjectRepo
from src.users.constants import UserStatus, UserType, UserPinningStatusType, OriginType
from src.users.entities import BaseUserCase
from src.users.exceptions import CheckNotFoundError, UserEmailTakenError, UserNotUnique
from src.users.models import RequestAssignClient, ResponseAssignClient
from src.users.repos import (
    Check,
    CheckRepo,
    User,
    UserRepo,
    UserRoleRepo,
    ConfirmClientAssignRepo,
    UserPinningStatusRepo,
    UniqueStatus, ConsultationTypeRepo, AmoCrmCheckLog
)
from src.users.types import UserHasher
from src.users.loggers.wrappers import user_changes_logger
from src.users.utils import get_unique_status


class LeadStatuses(IntEnum):
    """
     Статусы закрытых сделок в амо.
    """
    REALIZED: int = 142  # Успешно реализовано
    UNREALIZED: int = 143  # Закрыто и не реализовано


class AssignClientCase(BaseUserCase):
    """
    Кейс для закрепления клиента за агентом
    """

    client_tag: list[str] = ['клиент']
    lk_broker_tag: list[str] = ['ЛК Брокера']
    aggregator_tag: list[str] = ['Агрегатор']
    lk_test_tag: list[str] = ['Тест']
    dev_test_booking_tag: list[str] = ['Тестовая бронь']
    stage_test_booking_tag: list[str] = ['Тестовая бронь Stage']
    aggregator_slug = "aggregator"
    mail_event_slug = "assign_client"
    previous_agent_email_slug = "previous_agent_email"
    sms_event_slug = "assign_client"
    ORIGIN: str = OriginType.AGENT_ASSIGN
    user_client_type: str = UserType.CLIENT

    def __init__(
            self,
            user_repo: type[UserRepo],
            user_role_repo: type[UserRoleRepo],
            check_repo: type[CheckRepo],
            project_repo: type[ProjectRepo],
            booking_repo: type[BookingRepo],
            amo_statuses_repo: type[AmoStatusesRepo],
            template_repo: type[AssignClientTemplateRepo],
            confirm_client_assign_repo: type[ConfirmClientAssignRepo],
            booking_fixing_condition_repo: type[BookingFixingConditionsMatrixRepo],
            user_pinning_repo: type[UserPinningStatusRepo],
            consultation_type_repo: type[ConsultationTypeRepo],
            amocrm_log_repo: type[AmoCrmCheckLog],
            email_class: type[AgentEmail],
            amocrm_class: type[AmoCRM],
            sms_class: type[AgentSms],
            create_task_instance_service: CreateTaskInstanceService,
            hasher: Callable[..., UserHasher],
            amocrm_config: dict[Any, Any],
            request: Request,
            site_config: dict,
            get_email_template_service: GetEmailTemplateService,
            logger: Optional[Any] = structlog.getLogger(__name__),
    ):
        self.user_repo: UserRepo = user_repo()
        self.user_role_repo: UserRoleRepo = user_role_repo()
        self.check_repo: CheckRepo = check_repo()
        self.project_repo: ProjectRepo = project_repo()
        self.booking_repo: BookingRepo = booking_repo()
        self.user_pinning_repo: UserPinningStatusRepo = user_pinning_repo()
        self.amo_statuses_repo: AmoStatusesRepo = amo_statuses_repo()
        self.template_repo: AssignClientTemplateRepo = template_repo()
        self.confirm_client_assign_repo: ConfirmClientAssignRepo = confirm_client_assign_repo()
        self.booking_fixing_condition_repo: BookingFixingConditionsMatrixRepo = booking_fixing_condition_repo()
        self.consultation_type_repo: ConsultationTypeRepo = consultation_type_repo()
        self.amocrm_log_repo: AmoCrmCheckLog = amocrm_log_repo()
        self.email_class: Type[AgentEmail] = email_class
        self.amocrm_class: Type[AmoCRM] = amocrm_class
        self.sms_class: Type[AgentSms] = sms_class
        self.get_email_template_service: GetEmailTemplateService = get_email_template_service
        self.create_task_instance_service: CreateTaskInstanceService = create_task_instance_service
        self.hasher: UserHasher = hasher()
        self.main_site_host = site_config['main_site_host']
        self.partition_limit: int = amocrm_config["partition_limit"]
        self.site_host: str = site_config["site_host"]
        self.request = request
        self.logger = logger

        self.client_fetch_or_create = user_changes_logger(
            self.user_repo.fetch_or_create, self, content="Создание клиента, если не существует"
        )
        self.client_update = user_changes_logger(
            self.user_repo.update, self, content="Импортирование всех сделок пользователей в бд"
        )
        self.client_assign = user_changes_logger(
            self.user_repo.update, self, content="Закрепление клиента за агентом"
        )
        self.booking_create: Callable = booking_changes_logger(
            self.booking_repo.create, self, content="Создание сделки",
        )
        self.booking_bulk_update: Callable = booking_changes_logger(
            self.booking_repo.bulk_update, self, content="Обновляем все активные сделки клиента, закрепляем за агентом",
        )
        self.booking_update: Callable = booking_changes_logger(
            self.booking_repo.update, self, content="Обновление бронирования из сделок Амо",
        )

    async def _get_agency_realtor(self, agent_id, repres_id):
        if agent_id:
            filters: dict[str: Any] = dict(type=UserType.AGENT, id=agent_id)
        else:
            filters: dict[str: Any] = dict(type=UserType.REPRES, id=repres_id)

        agency_realtor: User = await self.user_repo.retrieve(
            filters=filters,
            prefetch_fields=['agency', 'agency__general_type', 'agent'],
        )

        return agency_realtor

    async def _get_client(self, payload):
        client_id_filters: dict[str: Any] = dict(type=UserType.CLIENT, id=payload.user_id)
        client: User = await self.user_repo.retrieve(filters=client_id_filters)

        if not client:
            user_data = payload.user_data
            user_data.update(dict(role=await self.user_role_repo.retrieve(filters=dict(slug=self.user_client_type))))
            client: User = await self.client_fetch_or_create(data=user_data)

        return client

    async def _add_comment(self, client, payload):
        filters = dict(slug=payload.consultation_type)
        consultation_type = await self.consultation_type_repo.retrieve(filters=filters)
        message = f"{consultation_type.name}"
        if payload.assignation_comment:
            message += f": {payload.assignation_comment}"
        async with await self.amocrm_class() as amocrm:

            amocrm_response = await amocrm.send_contact_note(
                contact_id=client.amocrm_id, message=message[:100])
            await self.amocrm_log_repo.create(**amocrm_response)

    async def __call__(
        self,
        payload: RequestAssignClient,
        agent_id: Optional[int] = None,
        repres_id: Optional[int] = None,
    ) -> ResponseAssignClient:

        agency_realtor = await self._get_agency_realtor(agent_id, repres_id)
        client = await self._get_client(payload)
        if not payload.email:
            payload.email = client.email

        await asyncio.gather(
            self._check_email_exists(email=payload.email, client=client),
            self._check_user_is_unique(
                check_id=payload.check_id,
                client_id=client.id,
                agent=agency_realtor,
            ),
        )

        un_assignation_link = self.generate_unassign_link(
            agent_id=agency_realtor.id,
            client_id=client.id,
        )

        if payload.agency_contact:
            agent_name = payload.agency_contact
        else:
            agent_name = agency_realtor.full_name

        notify_tasks: list[Awaitable] = []
        if client.agent_id and client.agent_id != agency_realtor.id:
            # Именно смене агентов, т.е. когда 1 агент меняется на другого.
            await client.fetch_related('agent')
            await self._send_email(
                recipients=[client.agent.email],
                agent_name=client.agent.full_name,
                client_name=client.full_name,
                slug=self.previous_agent_email_slug,
            )

        client = await self._update_client_data(
            client=client,
            agent=agency_realtor,
            payload=payload,
        )

        created_booking_id = await self._amocrm_hook(payload=payload, client=client, agent=agency_realtor)

        notify_tasks += [
            self._notify_client_sms(
                client_id=client.id,
                un_assignation_link=un_assignation_link,
                agent_name=agent_name,
            ),
            self._send_email(
                recipients=[client.email],
                agent_name=agent_name,
                unassign_link=unquote(un_assignation_link),
                slug=self.mail_event_slug,
            ),
        ]
        await asyncio.gather(
            *notify_tasks,
            self._set_pinning_status(client=client),
        )
        await self._add_comment(client, payload)

        client.booking_id = created_booking_id

        return ResponseAssignClient.from_orm(client)

    async def _amocrm_hook(self, payload: RequestAssignClient, client: User, agent: User) -> Optional[int]:
        """
        Сначала находим контакт пользователя в амо, если его нет создаём.
        Потом находим все сделки пользователя, импортируем в бд.
        Проставляем всем сделкам в амо и в бд агента из запроса, нужный статус.
        Потом проверяем на ЖК/Проекты из запроса, если нужно - создаём сделки в амо и в бд
        или возвращаем существующую если она подходит (для избегания "дублей").
        @param payload: RequestAssignClient
        @param client: User
        """
        async with await self.amocrm_class() as amocrm:
            contact: AmoContact = await self._get_or_create_amo_contact(
                amocrm,
                payload=payload,
                client=client,
                agent_id=agent.id,
            )
            await self.client_update(client, data=dict(amocrm_id=contact.id))
            contact_leads: list[AmoLead] = await self._fetch_contact_leads(amocrm, contact=contact)
            await self._import_amo_leads(
                client=client, agent=agent, active_projects=payload.active_projects, leads=contact_leads
            )
            await self._update_amocrm_leads(amocrm, leads=contact_leads, agent=agent, user=client)
            await self._update_booking_data(client=client, agent=agent)
            not_created_projects: list[Project] = await self._find_not_created_projects(
                client=client, agent_id=agent.id, payload=payload
            )

            if not_created_projects:
                result_booking_id = await self._create_requested_leads(
                    amocrm,
                    client=client,
                    not_created_projects=not_created_projects,
                    agent=agent,
                    consultation_type=payload.consultation_type,
                )
            else:
                result_booking_id = await self._get_existed_booking(
                    client=client, agent_id=agent.id, payload=payload
                )

            return result_booking_id

    async def _check_user_is_unique(self, check_id: int, client_id: int, agent: User):
        """
        Сравнение статуса последней проверки.
        Если проверки нет - возвращаем ошибку.
        Если статус проверки not_unique возвращаем ошибку.
        @rtype: bool
        """
        filters: dict[str, Any] = {'id': check_id}
        check: Check = await self.check_repo.retrieve(filters=filters, ordering='-id', related_fields=["unique_status"])
        if not check:
            raise CheckNotFoundError
        if check.unique_status.slug != UserStatus.UNIQUE:
            raise UserNotUnique
        data = dict(
            user_id=client_id,
            agent_id=agent.id,
            dispute_agent_id=None,
            agency_id=agent.agency_id,
            status_fixed=False
        )
        await self.check_repo.update(check, data=data)

    async def _check_email_exists(self, email: str, client: User):
        """
        Если у пользователя и в запросе не совпадает почта и она уже есть в бд - возвращаем ошибку.
        @param email: str
        @param client: User
        """
        if client.email != email:
            filters: dict[str, Any] = {'email__iexact': email, "type": UserType.CLIENT}
            if await self.user_repo.exists(filters=filters):
                raise UserEmailTakenError


    async def _get_or_create_amo_contact(
        self,
        amocrm: AmoCRM,
        payload: RequestAssignClient,
        client: User,
        agent_id: int,
    ) -> AmoContact:
        """
        Находим контакт в амо или создаём его. Если несколько контактов - сортируем по дате создания
        и возвращаем самый последний.
        @param payload: pydantic объект запроса.
        @return: AmoContact (Контакт пользователя в схеме Pydantic).
        """
        amocrm_id = client.amocrm_id
        if not amocrm_id:
            contacts: list[AmoContact] = await amocrm.fetch_contacts(
                user_phone=client.phone,
                query_with=[AmoContactQueryWith.leads],
            )
            if contacts:
                amocrm_id: int = contacts[0].id
            else:
                created_contact: list[dict] = await amocrm.create_contact_v4(
                    user_phone=payload.phone,
                    user_email=payload.email,
                    user_name=payload.full_name,
                    first_name=payload.name,
                    last_name=payload.surname,
                    creator_user_id=agent_id,
                    tags=self.client_tag + self.lk_broker_tag
                )
                amocrm_id: int = created_contact[0].get('id')
        contact: AmoContact = await amocrm.fetch_contact(
            user_id=amocrm_id, query_with=[AmoContactQueryWith.leads]
        )
        return contact

    async def _fetch_contact_leads(self, amocrm: AmoCRM, contact: AmoContact) -> list[AmoLead]:
        """
        Найти сделки контакта в амо
        @param contact: AmoContact
        @return: list[AmoLead]
        """
        big_lead_ids: list[int] = [lead.id for lead in contact.embedded.leads]
        if not big_lead_ids:
            return []
        leads = []
        for lead_ids in partition_list(big_lead_ids, self.partition_limit):
            leads.extend(await amocrm.fetch_leads(lead_ids=lead_ids, query_with=[AmoLeadQueryWith.contacts]))
        return leads

    async def _update_client_data(self, agent: User, client: User, payload: RequestAssignClient) -> User:
        """
        Закрепить клиента за агентом.
        @param agent: User (Модель агента, от лица которого мы закрепляем клиента).
        @param client: User(Модель клиента, которого мы закрепляем за агентом).
        @return: User (client)
        """
        project: Optional[Project] = await self._get_project_from_payload(payload=payload)
        data: dict[str, Any] = dict(
            agent=agent,
            agency=agent.agency,
            work_start=datetime.now(tz=UTC).date(),
            interested_project=project,
            origin=self.ORIGIN,
        )
        client: User = await self.client_assign(
            client, data=dict(**payload.user_data, **data)
        )
        asyncio.create_task(
            self._set_assigned_time(client=client, agent=agent,
                                    comment=f"{payload.consultation_type}: {payload.assignation_comment}")
        )
        return client

    async def _set_assigned_time(self, client: User, agent: User, comment: Optional[str] = None) -> None:
        """
        Установить время привязки/перепривязки клиента к агенту
        @param client: User
        @param agent: User
        """
        data: dict[str, Any] = dict(
            client=client,
            agent=agent,
            agency=agent.agency,
            comment=comment,
        )
        await self.confirm_client_assign_repo.create(data=data)

    async def _get_project_from_payload(self, payload: RequestAssignClient) -> Optional[Project]:
        """
        Получить проект из запроса
        @param payload: RequestAssignClient
        @return: Project
        """
        project: Optional[Project] = None
        if payload.active_projects:
            project: Project = await self.project_repo.retrieve(filters=dict(id=payload.active_projects[0])).only("id")
        return project

    async def _import_amo_leads(
        self, client: User, agent: User, active_projects: list[int], leads: list[AmoLead]
    ) -> None:
        """
        Импортируем сделки из Амо.
        Тут импортируются только активные сделки пользователя из амо для проектов,
        которые переданы в active_projects.
        @param active_projects: list[int]. Список ЖК/Проектов из запроса.
        @param client: User
        @param leads: list[AmoLead]. Список сделок клиента из амо.
        """
        queryset = self.project_repo.list()
        active_pipeline_ids: list[str] = await self.project_repo.facets(
            field='amo_pipeline_id', queryset=queryset, filters=dict(id__in=active_projects)
        )
        active_pipeline_ids: set[int] = set(map(int, active_pipeline_ids))
        need_import_leads: list[AmoLead] = list(
            filter(lambda x: x.pipeline_id in active_pipeline_ids, leads)
        )
        await self._update_create_leads_bookings(leads=need_import_leads, client=client, agent=agent)

    async def _update_create_leads_bookings(self, leads: list[AmoLead], client: User, agent: User):
        """
        Создаём или обновляем бронирования из сделок Амо.
        @param leads: list[AmoLead]. Список сделок, которые мы хотим создать
        @param client: User
        @return: list[Bookings]
        """
        for lead in leads:
            if lead.status_id in (LeadStatuses.REALIZED, LeadStatuses.UNREALIZED):
                continue

            amocrm_name: list = [custom_field.values[0].value for custom_field in lead.custom_fields_values if
                                 custom_field.field_id == self.amocrm_class.project_field_id]
            if amocrm_name:
                project: Project = await self.project_repo.retrieve(
                    filters=dict(
                        amo_pipeline_id=lead.pipeline_id,
                        amocrm_name=amocrm_name[0],
                        status=ProjectStatus.CURRENT,
                    )
                )
            else:
                project = None

            amocrm_substage: str = self.amocrm_class.get_lead_substage(lead.status_id)
            amocrm_stage: str = BookingStagesMapping()[amocrm_substage]
            status: AmocrmStatus = await self.amo_statuses_repo.retrieve(filters=dict(id=lead.status_id))
            data: dict[str, Any] = dict(
                tags=[tag.name for tag in lead.embedded.tags],
                amocrm_stage=amocrm_stage,
                amocrm_substage=amocrm_substage,
                project=project,
                user=client,
                agent_id=agent.id,
                agency_id=agent.agency_id,
                amocrm_status_id=lead.status_id,
                amocrm_status=status,
            )

            booking = await self.booking_repo.retrieve(filters=dict(amocrm_id=lead.id))
            if booking:
                booking = await self.booking_update(booking=booking, data=data)
                booking_created: bool = False
            else:
                booking_source: BookingSource = await get_booking_source(slug=BookingCreatedSources.AMOCRM)
                data.update(
                    amocrm_id=lead.id,
                    created_source=BookingCreatedSources.AMOCRM,  # todo: deprecated
                    booking_source=booking_source,
                )
                booking = await self.booking_create(data=data)
                booking_created: bool = True

            self.logger.info(f"Booking taste case 1: {booking.id}, {booking.active}, {booking.amocrm_status}")
            await self._create_task_instance([booking.id], booking_created=booking_created)

    async def _find_not_created_projects(
        self,
        client: User,
        agent_id: int,
        payload: RequestAssignClient,
    ) -> list[Project]:
        """
        Проверяем нет ли уже нужной сделки в указанном проекте
        @param client: User
        @param payload: RequestAssignClient
        @return: list[Project]
        """
        filters: dict[str, Any] = dict(
            active=True,
            user_id=client.id,
            agent_id=agent_id,
            amocrm_stage=BookingStages.START,
            amocrm_substage=BookingSubstages.ASSIGN_AGENT,
        )
        bookings: list[Booking] = await self.booking_repo.list(filters=filters)
        booking_projects: set = {booking.project_id for booking in bookings}
        not_created_project_ids = set(payload.active_projects).difference(booking_projects)
        return await self.project_repo.list(
            filters=dict(id__in=not_created_project_ids),
            related_fields=["city"]
        )

    async def _create_requested_leads(
        self,
        amocrm: AmoCRM,
        client: User,
        not_created_projects: list[Project],
        agent: User,
        consultation_type: str,
    ) -> Optional[int]:
        """
        Создаём сделки в амо в тех воронках, которые переданы в запросе, если таких сделок ещё нет.
        Создаём так-же в бд.
        @param client: User
        @param not_created_projects: list[Project]
        """
        status_name: str = 'фиксация клиента за ан'
        tags: list[str] = self.lk_broker_tag + self.lk_test_tag if client.is_test_user else self.lk_broker_tag
        if agent.agency and agent.agency.general_type and agent.agency.general_type.slug == self.aggregator_slug:
            tags = tags + self.aggregator_tag

        if maintenance_settings["environment"] == EnvTypes.DEV:
            tags = tags + self.dev_test_booking_tag
        elif maintenance_settings["environment"] == EnvTypes.STAGE:
            tags = tags + self.stage_test_booking_tag

        created_booking_id: Optional[int] = None
        for project in not_created_projects:
            status, amo_pipeline_id, amo_responsible_user_id = await self._get_data_for_create_lead(
                project=project,
                consultation_type=consultation_type,
            )
            if status is None:
                status: AmocrmStatus = await self._get_status_by_name(
                    name=status_name,
                    pipeline_id=project.amo_pipeline_id,
                )
            if amo_pipeline_id is None:
                amo_pipeline_id = project.amo_pipeline_id
            if amo_responsible_user_id is None:
                amo_responsible_user_id = project.amo_responsible_user_id
            if status is None:
                self.logger.error(
                    f'Не удалось найти статус "{status_name}" для проекта {project}  в БД!',
                    project=project.id)
                continue

            amo_data = dict(
                status_id=status.id,
                city_slug=project.city.slug,
                property_id=None,
                property_type=None,
                user_amocrm_id=client.amocrm_id,
                lead_name=create_lead_name(client),
                project_amocrm_name=project.amocrm_name,
                project_amocrm_enum=project.amocrm_enum,
                project_amocrm_organization=project.amocrm_organization,
                project_amocrm_pipeline_id=amo_pipeline_id,
                project_amocrm_responsible_user_id=amo_responsible_user_id,
                contact_ids=[agent.amocrm_id],
                companies=[agent.agency.amocrm_id],
                creator_user_id=agent.id,
                tags=tags,
                is_agency_deal=True,
            )
            print(f"New lead AMO data: {amo_data}")
            lead: list[AmoLead] = await amocrm.create_lead(**amo_data)
            booking_source: BookingSource = await get_booking_source(slug=BookingCreatedSources.LK_ASSIGN)
            lead_amocrm_id = lead[0].id
            booking = await self.booking_repo.retrieve(filters=dict(amocrm_id=lead_amocrm_id))
            data: dict[str, Any] = dict(
                amocrm_id=lead_amocrm_id,
                amocrm_stage=BookingStages.START,
                amocrm_substage=BookingSubstages.ASSIGN_AGENT,
                project=project,
                user=client,
                agent=agent,
                agency=agent.agency,
                amocrm_status_id=status.id,
                amocrm_status=status,
                origin=f"https://{self.site_host}",
                created_source=BookingCreatedSources.LK_ASSIGN,  # todo: deprecated
                booking_source=booking_source,
                tags=tags,
                active=True,
            )
            if booking:
                booking = await self.booking_update(booking=booking, data=data)
                booking_created: bool = False
            else:
                booking = await self.booking_create(data=data)
                booking_created: bool = True

            await booking.refresh_from_db(fields=["id"])
            self.logger.info(f"Booking taste case 2: {booking.id}, {booking.active}, {booking.amocrm_status}")
            await self._create_task_instance([booking.id], booking_created=booking_created)
            created_booking_id = booking.id

        return created_booking_id

    async def _get_existed_booking(
        self,
        client: User,
        agent_id: int,
        payload: RequestAssignClient,
    ) -> int | None:
        filters: dict[str, Any] = dict(
            active=True,
            user_id=client.id,
            agent_id=agent_id,
            amocrm_stage=BookingStages.START,
            amocrm_substage=BookingSubstages.ASSIGN_AGENT,
            project_id__in=payload.active_projects,
        )
        booking: Booking | None = await self.booking_repo.list(filters=filters).first()

        if booking:
            return booking.id

    async def _get_data_for_create_lead(
            self,
            project: Project,
            consultation_type: str,
    ) -> tuple[AmocrmStatus | None, int | None, str | None]:
        """
        Получение данных из матрицы для создания сделки
        """
        booking_fixing_condition: BookingFixingConditionsMatrix = \
            await self.booking_fixing_condition_repo.list(
                filters=dict(
                    project=project,
                    created_source=BookingCreatedSources.LK_ASSIGN,
                    consultation_type__slug=consultation_type,
                )
            ).first()
        if booking_fixing_condition:
            await booking_fixing_condition.fetch_related('pipelines')
            group_status: AmocrmGroupStatus = await booking_fixing_condition.status_on_create
            pipelines: list[AmocrmPipeline] = booking_fixing_condition.pipelines
            amo_responsible_user_id = booking_fixing_condition.amo_responsible_user_id

            statuses = await group_status.statuses
            pipeline_id: str = str(pipelines[0].id) if pipelines else project.amo_pipeline_id

            status_on_create = next(
                (status for status in statuses
                 if str(status.pipeline_id) == pipeline_id), None)

            return status_on_create, pipeline_id, amo_responsible_user_id

        else:
            return None, None, None

    async def _get_status_by_name(self, name: str, pipeline_id: Union[str, int]) -> Optional[AmocrmStatus]:
        """
        @param pipeline_id: int. ID воронки
        @return: Optional[AmocrmStatus]
        """
        filters = dict(name__icontains=name, pipeline_id=pipeline_id)
        status: Optional[AmocrmStatus] = await self.amo_statuses_repo.retrieve(filters=filters)
        return status

    async def _update_booking_data(self, client: User, agent: User):
        """
        Обновляем все активные сделки клиента, закрепляем за агентом.
        Ставим статус сделки "Закрепление за АН"
        @param client: User
        @param agent: User
        """
        filters: dict[str, Any] = dict(user_id=client.id, active=True)
        exclude_filters: list[dict] = [
            dict(amocrm_status_id=LeadStatuses.REALIZED),
            dict(amocrm_status_id=LeadStatuses.UNREALIZED),
        ]
        data = dict(
            agent_id=agent.id,
            agency_id=agent.agency.id,
            active=True,
        )
        await self.booking_bulk_update(filters=filters, exclude_filters=exclude_filters, data=data)
        bookings: list[Booking] = await self.booking_repo.list(filters=filters).exclude(
            amocrm_status_id=LeadStatuses.REALIZED
        ).exclude(
            amocrm_status_id=LeadStatuses.UNREALIZED
        )
        if bookings:
            self.logger.info(f"Booking taste case 3: {[booking.id for booking in bookings]}, "
                             f"{[booking.active for booking in bookings]},"
                             f" {[booking.amocrm_status for booking in bookings]}")
            await self._create_task_instance([booking.id for booking in bookings])

    async def _update_amocrm_leads(self, amocrm: AmoCRM, leads: list[AmoLead], agent: User, user: User):
        """
        @param leads: list[AmoLead]. Список сделок амоцрм.
        """
        # получаем все сделки клиента, кроме закрытых и реализованных
        active_leads = [
            lead for lead in leads if lead.status_id not in (
                LeadStatuses.REALIZED,
                LeadStatuses.UNREALIZED
            )
        ]
        active_leads_ids: list[int] = [lead.id for lead in active_leads]

        # находим amocrm_id всех старых агентов и старых агентств в сделках клиента в амо
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

        for lead_id in active_leads_ids:
            await amocrm.update_lead(lead_id=lead_id, is_agency_deal=True)

    async def _notify_client_sms(
        self,
        client_id: int,
        un_assignation_link: str,
        agent_name: str,
    ) -> None:
        """
        Отправляем уведомление клиенту.
        @param client_id: int
        @param un_assignation_link: str
        @param agent_name: str
        """
        client: User = await self.user_repo.retrieve(
            filters=dict(id=client_id),
            related_fields=[
                "interested_project",
                "interested_project__city",
            ],
        )

        if not client.interested_project:
            return

        city: City = client.interested_project.city

        if city.slug == "moskva":
            #  Для клиентов МСК перенести смс на этап постановки брони.
            return

        template: AssignClientTemplate = await self.template_repo.retrieve(
            filters=dict(
                city=city,
                sms__sms_event_slug=self.sms_event_slug,
                sms__is_active=True,
                is_active=True,
            ),
            related_fields=["sms"],
        )
        if template and not template.is_active:
            # Если шаблон есть, но он не активен, то не отправляем смс
            return

        if not template:
            template: AssignClientTemplate = await self.template_repo.retrieve(
                filters=dict(default=True, sms__is_active=True, is_active=True),
                related_fields=["sms"],
            )
        if not template:
            # Если нет активного шаблона, то не отправляем смс
            return

        await self._send_sms(
            phone=client.phone,
            unassign_link=un_assignation_link,
            agent_name=agent_name,
            sms_template=template.sms.template_text,
        )
        await self.user_repo.update(model=client, data=dict(sms_send=True))

    async def _send_email(self, recipients: list[str], slug, **context) -> Task:
        """
        Отправляем письмо клиенту.
        @param recipients: list[str]
        @param context: Any (Контекст, который будет использоваться в шаблоне письма)
        @return: Task
        """
        email_notification_template = await self.get_email_template_service(
            mail_event_slug=slug,
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

    async def _send_sms(self, phone: str, unassign_link: str, agent_name: str, sms_template: str):
        """
        Отправляем смс клиенту.
        @param phone: str
        @param unassign_link: str
        @param agent_name: str
        """
        sms_options: dict[str, Any] = dict(
            phone=phone,
            message=sms_template.format(unassign_link=unassign_link, agent_name=agent_name),
            tiny_url=True,
        )
        return self.sms_class(**sms_options).as_task()

    async def _create_task_instance(self, booking_ids: list[int], booking_created: bool = False) -> None:
        """
        Создаем задачу на создание экземпляра задачи.
        @param booking_ids: list[int]
        """
        task_context: CreateTaskDTO = CreateTaskDTO()
        task_context.booking_created = booking_created
        task_context.is_main = True
        await self.create_task_instance_service(booking_ids=booking_ids, task_context=task_context)

    def generate_tokens(self, agent_id: int, client_id: int) -> Tuple[str, str]:
        """generate_tokens"""
        data = json.dumps(dict(agent_id=agent_id, client_id=client_id))
        b64_data = b64encode(data.encode()).decode()
        b64_data = b64_data.replace("&", "%26")
        token = self.hasher.hash(b64_data)
        return b64_data, token

    def generate_unassign_link(self, agent_id: int, client_id: int) -> str:
        """
        Генерация ссылки для страницы открепления клиента от юзера
        @param agent_id: int
        @param client_id: int
        @return: str
        """
        b64_data, token = self.generate_tokens(agent_id=agent_id, client_id=client_id)
        return f"https://{self.main_site_host}/unassign?t={token}%26d={b64_data}"

    async def _set_pinning_status(self, client: User) -> None:
        """
        Устанавливаем статус закрепления для клиента.
        @param client: User
        """
        unique_status: UniqueStatus = await get_unique_status(slug=UserPinningStatusType.PARTIALLY_PINNED)
        await self.user_pinning_repo.update_or_create(
            filters=dict(user=client), data=dict(unique_status=unique_status)
        )
