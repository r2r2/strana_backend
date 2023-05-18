# pylint: disable=missing-param-doc,missing-raises-doc,redundant-returns-doc
import asyncio
import json
from asyncio import Task
from base64 import b64encode
from datetime import datetime
from urllib.parse import unquote
from enum import Enum
from typing import Any, Callable, Optional, Tuple, Type, Union

import structlog
from pytz import UTC
from fastapi import Request

from common.amocrm import AmoCRM
from common.amocrm.constants import AmoContactQueryWith
from common.amocrm.repos import AmoStatusesRepo
from common.amocrm.types import AmoContact, AmoLead
from common.backend.models import AmocrmStatus
from common.email import EmailService
from common.utils import partition_list
from src.agents.types import AgentEmail, AgentSms
from src.booking.constants import BookingCreatedSources, BookingStages, BookingStagesMapping, BookingSubstages
from src.booking.repos import Booking, BookingRepo
from src.booking.loggers import booking_changes_logger
from src.cities.repos import City
from src.notifications.repos import AssignClientTemplate, AssignClientTemplateRepo
from src.projects.repos import Project, ProjectRepo
from src.users.constants import UserStatus, UserType
from src.users.entities import BaseUserCase
from src.users.exceptions import CheckNotFoundError, UserAlreadyBoundError, UserEmailTakenError, UserNotUnique
from src.users.models import RequestAssignClient, ResponseAssignClient
from src.users.repos import Check, CheckRepo, User, UserRepo
from src.users.types import UserHasher
from ..loggers.wrappers import user_changes_logger
from ...notifications.exceptions import SMSTemplateNotFoundError
from ...task_management.services import CreateTaskInstanceService


class LeadStatuses(int, Enum):
    """
     Статусы закрытых сделок в амо.
    """
    REALIZED: int = 142  # Успешно реализовано
    UNREALIZED: int = 143  # Закрыто и не реализовано


class AssignClientCase(BaseUserCase):
    """
    Кейс для закрепления клиента за агентом
    """

    email_template: str = 'src/users/templates/agent_assign_client.html'
    client_tag: list[str] = ['клиент']
    lk_broker_tag: list[str] = ['ЛК Брокера']
    sms_event_slug = "assign_client"

    def __init__(
        self,
        user_repo: Type[UserRepo],
        check_repo: Type[CheckRepo],
        project_repo: Type[ProjectRepo],
        booking_repo: Type[BookingRepo],
        amo_statuses_repo: Type[AmoStatusesRepo],
        template_repo: Type[AssignClientTemplateRepo],
        email_class: Type[AgentEmail],
        amocrm_class: Type[AmoCRM],
        sms_class: Type[AgentSms],
        create_task_instance_service: CreateTaskInstanceService,
        hasher: Callable[..., UserHasher],
        amocrm_config: dict[Any, Any],
        request: Request,
        site_config: dict,
        logger: Optional[Any] = structlog.getLogger(__name__),
    ):
        self.user_repo: UserRepo = user_repo()
        self.check_repo: CheckRepo = check_repo()
        self.project_repo: ProjectRepo = project_repo()
        self.booking_repo: BookingRepo = booking_repo()
        self.amo_statuses_repo: AmoStatusesRepo = amo_statuses_repo()
        self.template_repo: AssignClientTemplateRepo = template_repo()
        self.email_class: Type[AgentEmail] = email_class
        self.amocrm_class: Type[AmoCRM] = amocrm_class
        self.sms_class: Type[AgentSms] = sms_class
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
        self.booking_update_or_create: Callable = booking_changes_logger(
            self.booking_repo.update_or_create, self, content="Создание или обновление бронирования из сделок Амо",
        )

    async def __call__(self, payload: RequestAssignClient, agent_id: int) -> ResponseAssignClient:
        filters: dict[str: Any] = dict(type=UserType.AGENT, id=agent_id)
        agent: User = await self.user_repo.retrieve(filters=filters, prefetch_fields=['agency'])
        client_id_filters: dict[str: Any] = dict(type=UserType.CLIENT, id=payload.user_id)
        client: User = await self.user_repo.retrieve(filters=client_id_filters)
        if not client:
            client: User = await self.client_fetch_or_create(data=payload.user_data)

        if not payload.email:
            payload.email = client.email

        await asyncio.gather(
            self._check_email_exists(email=payload.email, client=client),
            self._check_user_is_unique(check_id=payload.check_id, client_id=client.id, agent=agent),
            self._check_user_already_assigned(agent_id=agent.id, client=client),
        )
        await self._amocrm_hook(payload=payload, client=client, agent=agent)

        un_assignation_link = self.generate_unassign_link(agent_id=agent.id, client_id=client.id)

        if payload.agency_contact:
            agent_name = payload.agency_contact
        else:
            agent_name = agent.full_name

        client = await self._update_client_data(client=client, agent=agent, payload=payload)

        await self._notify_client_sms(
            client_id=client.id,
            un_assignation_link=un_assignation_link,
            agent_name=agent_name,
        )

        await self._send_email(
            recipients=[client.email], agent_name=agent_name, unassign_link=unquote(un_assignation_link)
        )

        if payload.assignation_comment:
            async with await self.amocrm_class() as amocrm:
                await amocrm.send_contact_note(contact_id=client.id, message=payload.assignation_comment)
        return ResponseAssignClient.from_orm(client)

    async def _amocrm_hook(self, payload: RequestAssignClient, client: User, agent: User) -> None:
        """
        Сначала находим контакт пользователя в амо, если его нет создаём.
        Потом находим все сделки пользователя, импортируем в бд.
        Проставляем всем сделкам в амо и в бд агента из запроса, нужный статус.
        Потом проверяем на ЖК/Проекты из запроса, если нужно - создаём сделки в амо и в бд.
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
            await self._import_amo_leads(client=client, agent=agent, active_projects=payload.active_projects,
                                         leads=contact_leads)
            await self._update_amocrm_leads(amocrm, leads=contact_leads, agent=agent)
            await self._update_booking_data(client=client, agent=agent)
            not_created_projects: list[Project] = await self._find_not_created_projects(client=client,
                                                                                        agent_id=agent.id,
                                                                                        payload=payload)
            await self._create_requested_leads(
                amocrm,
                client=client,
                not_created_projects=not_created_projects,
                agent=agent,
            )

    async def _check_user_is_unique(self, check_id: int, client_id: int, agent: User):
        """
        Сравнение статуса последней проверки.
        Если проверки нет - возвращаем ошибку.
        Если статус проверки not_unique возвращаем ошибку.
        @rtype: bool
        """
        filters: dict[str, Any] = {'id': check_id}
        check: Check = await self.check_repo.retrieve(filters=filters, ordering='-id')
        if not check:
            raise CheckNotFoundError
        if check.status != UserStatus.UNIQUE:
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

    @staticmethod
    async def _check_user_already_assigned(agent_id: int, client: User):
        """
        Проверка не был ли клиент привязан к агенту ранее
        @param agent_id:
        @param client:
        """
        if client.agent_id == agent_id:
            raise UserAlreadyBoundError

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
            created_contact: list[dict] = await amocrm.create_contact(
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
            leads.extend(await amocrm.fetch_leads(lead_ids=lead_ids))
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
        )
        client: User = await self.client_assign(
            client, data=dict(**payload.user_data, **data)
        )
        return client

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

            amocrm_name: str = [custom_field.values[0].value for custom_field in lead.custom_fields_values if custom_field.field_id == self.amocrm_class.project_field_id][0]
            project: Project = await self.project_repo.retrieve(
                filters=dict(amo_pipeline_id=lead.pipeline_id, amocrm_name=amocrm_name)
            )
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
            booking = await self.booking_update_or_create(data=data, filters=dict(amocrm_id=lead.id))
            await booking.refresh_from_db(fields=["id"])
            await self._create_task_instance([booking.id])

    async def _find_not_created_projects(
            self, client: User, agent_id: int, payload: RequestAssignClient) -> list[Project]:
        """
        Находим не созданные в бд сделки, исходя из переданных в запросе id проектов.
        @param client: User
        @param payload: RequestAssignClient
        @return: list[Project]
        """
        filters: dict[str, Any] = dict(active=True, user_id=client.id, agent_id=agent_id)
        bookings: list[Booking] = await self.booking_repo.list(filters=filters)
        booking_projects: set = {booking.project_id for booking in bookings}
        not_created_project_ids = set(payload.active_projects).difference(booking_projects)
        return await self.project_repo.list(
            filters=dict(id__in=not_created_project_ids),
            prefetch_fields=[
                dict(
                    relation="city",
                    queryset=City.all().only("slug"),
                ),
            ]
        )

    async def _create_requested_leads(
        self,
        amocrm: AmoCRM,
        client: User,
        not_created_projects: list[Project],
        agent: User,
    ):
        """
        Создаём сделки в амо в тех воронках, которые переданы в запросе, если таких сделок ещё нет.
        Создаём так-же в бд.
        @param client: User
        @param not_created_projects: list[Project]
        """
        status_name: str = 'фиксация клиента за ан'
        for project in not_created_projects:
            status: AmocrmStatus = await self._get_status_by_name(name=status_name, pipeline_id=project.amo_pipeline_id)
            if not status:
                self.logger.error(
                    f'Не удалось найти статус {status.name} в БД!', project=project.id)
                continue
            amo_data = dict(
                status_id=status.id,
                city_slug=project.city.slug,
                property_id=None,
                property_type=None,
                user_amocrm_id=client.amocrm_id,
                project_amocrm_name=project.amocrm_name,
                project_amocrm_enum=project.amocrm_enum,
                project_amocrm_organization=project.amocrm_organization,
                project_amocrm_pipeline_id=project.amo_pipeline_id,
                project_amocrm_responsible_user_id=project.amo_responsible_user_id,
                contact_ids=[agent.amocrm_id],
                companies=[agent.agency.amocrm_id],
                creator_user_id=agent.id,
                tags=self.lk_broker_tag,
            )
            print(f"New lead AMO data: {amo_data}")
            lead: list[AmoLead] = await amocrm.create_lead(**amo_data)
            lead_amocrm_id = lead[0].id
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
                created_source=BookingCreatedSources.LK_ASSIGN,
                tags=self.lk_broker_tag,
                active=True,
            )
            booking = await self.booking_create(data=data)
            await booking.refresh_from_db(fields=["id"])
            await self._create_task_instance([booking.id])

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
        data = dict(
            agent_id=agent.id,
            agency_id=agent.agency.id,
            active=True
        )
        await self.booking_bulk_update(filters=filters, data=data)
        bookings: list[Booking] = await self.booking_repo.list(filters=filters)
        if bookings:
            await self._create_task_instance([booking.id for booking in bookings])

    async def _update_amocrm_leads(self, amocrm: AmoCRM, leads: list[AmoLead], agent: User):
        """
        @param leads: list[AmoLead]. Список сделок амоцрм.
        """
        for lead in leads:
            if lead.status_id in (LeadStatuses.REALIZED, LeadStatuses.UNREALIZED):
                continue

            amo_data = dict(
                company=agent.agency.amocrm_id,
                lead_id=lead.id,
                contacts=[agent.amocrm_id],
            )
            await asyncio.create_task(
                amocrm.update_lead(**amo_data)
            )

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
            filters=dict(city=city, sms__sms_event_slug=self.sms_event_slug, sms__is_active=True)
        )
        if not template:
            raise SMSTemplateNotFoundError

        await self._send_sms(
            phone=client.phone,
            unassign_link=un_assignation_link,
            agent_name=agent_name,
            sms_template=template.sms.template_text,
        )
        await self.user_repo.update(model=client, data=dict(sms_send=True))

    async def _send_email(self, recipients: list[str], **context) -> Task:
        """
        Отправляем письмо клиенту.
        @param recipients: list[str]
        @param context: Any (Контекст, который будет использоваться в шаблоне письма)
        @return: Task
        """
        email_options: dict[str, Any] = dict(
            topic="Добро пожаловать в Страну!",
            template=self.email_template,
            recipients=recipients,
            context=context
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

    async def _create_task_instance(self, booking_ids: list[int]) -> None:
        """
        Создаем задачу на создание экземпляра задачи.
        @param booking_ids: list[int]
        """
        await self.create_task_instance_service(booking_ids=booking_ids)

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
