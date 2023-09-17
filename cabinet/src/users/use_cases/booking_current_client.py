# pylint: disable=missing-param-doc,missing-raises-doc,redundant-returns-doc
from enum import Enum
from typing import Any, Callable, Optional, Type, Union

import structlog
from common.amocrm import AmoCRM
from common.amocrm.constants import AmoContactQueryWith, AmoLeadQueryWith
from common.amocrm.repos import AmoStatusesRepo
from common.amocrm.types import AmoContact, AmoLead
from common.backend.models import AmocrmStatus
from common.utils import partition_list
from fastapi import Request
from src.booking.constants import (BookingCreatedSources, BookingStages,
                                   BookingStagesMapping, BookingSubstages)
from src.booking.loggers import booking_changes_logger
from src.booking.models import ResponseBookingRetrieveModel
from src.booking.repos import Booking, BookingRepo, BookingSource
from src.booking.utils import get_booking_source
from src.projects.repos import Project, ProjectRepo
from src.task_management.services import CreateTaskInstanceService
from src.users.constants import UserType
from src.users.entities import BaseUserCase
from src.users.exceptions import UserNotFoundError, UserAgentMismatchError
from src.users.models import RequestAssignClient, RequestBookingCurrentClient
from src.users.repos import CheckRepo, User, UserRepo
from src.users.services import CheckPinningStatusService


class LeadStatuses(int, Enum):
    """
     Статусы закрытых сделок в амо.
    """
    REALIZED: int = 142  # Успешно реализовано
    UNREALIZED: int = 143  # Закрыто и не реализовано


class BookingCurrentClientCase(BaseUserCase):
    """
    Кейс сделки действующего клиента за агентом
    """

    client_tag: list[str] = ['клиент']
    lk_broker_tag: list[str] = ['ЛК Брокера']
    lk_test_tag: list[str] = ['Тест']

    def __init__(
        self,
        user_repo: Type[UserRepo],
        check_repo: Type[CheckRepo],
        project_repo: Type[ProjectRepo],
        booking_repo: Type[BookingRepo],
        amo_statuses_repo: Type[AmoStatusesRepo],
        amocrm_class: Type[AmoCRM],
        create_task_instance_service: CreateTaskInstanceService,
        amocrm_config: dict[Any, Any],
        site_config: dict,
        check_pinning: CheckPinningStatusService,
        request: Request,
        logger: Optional[Any] = structlog.getLogger(__name__),
    ):
        self.user_repo: UserRepo = user_repo()
        self.check_repo: CheckRepo = check_repo()
        self.project_repo: ProjectRepo = project_repo()
        self.booking_repo: BookingRepo = booking_repo()
        self.amo_statuses_repo: AmoStatusesRepo = amo_statuses_repo()
        self.amocrm_class: Type[AmoCRM] = amocrm_class
        self.create_task_instance_service: CreateTaskInstanceService = create_task_instance_service
        self.check_pinning: CheckPinningStatusService = check_pinning
        self.partition_limit: int = amocrm_config["partition_limit"]
        self.site_host: str = site_config["site_host"]
        self.request = request,
        self.logger = logger

        self.booking_create: Callable = booking_changes_logger(
            self.booking_repo.create, self, content="Создание сделки",
        )
        self.booking_bulk_update: Callable = booking_changes_logger(
            self.booking_repo.bulk_update, self, content="Обновляем все активные сделки клиента, закрепляем за агентом",
        )
        self.booking_update: Callable = booking_changes_logger(
            self.booking_repo.update, self, content="Обновление бронирования из сделок Амо",
        )

    async def __call__(
        self,
        payload: RequestBookingCurrentClient,
        agent_id: Optional[int] = None,
        repres_id: Optional[int] = None,
    ) -> ResponseBookingRetrieveModel:

        if agent_id:
            filters: dict[str: Any] = dict(type=UserType.AGENT, id=agent_id)
        else:
            filters: dict[str: Any] = dict(type=UserType.REPRES, id=repres_id)

        agency_realtor: User = await self.user_repo.retrieve(filters=filters, prefetch_fields=['agency', 'agent'])

        client_id_filters: dict[str: Any] = dict(type=UserType.CLIENT, id=payload.user_id)
        client: User = await self.user_repo.retrieve(filters=client_id_filters)

        if not client:
            raise UserNotFoundError

        if (agent_id and client.agent_id != agency_realtor.id) or (
                repres_id and client.agency_id != agency_realtor.agency.id):
            raise UserAgentMismatchError

        booking = await self._amocrm_hook(payload=payload, client=client, agent=agency_realtor)
        booking.property = None

        return booking

    async def _amocrm_hook(self, payload: RequestBookingCurrentClient, client: User, agent: User) -> Booking:
        """
        Сначала находим контакт пользователя в амо, если его нет создаём.
        Потом находим все сделки пользователя, импортируем в бд.
        Проставляем всем сделкам в амо и в бд агента из запроса, нужный статус.
        Потом проверяем на ЖК/Проекты из запроса, если нужно - создаём сделки в амо и в бд.
        @param payload: RequestAssignClient
        @param client: User
        """
        async with await self.amocrm_class() as amocrm:
            # contact: AmoContact = await self._get_or_create_amo_contact(
            #     amocrm,
            #     payload=payload,
            #     client=client,
            #     agent_id=agent.id,
            # )
            # contact_leads: list[AmoLead] = await self._fetch_contact_leads(amocrm, contact=contact)
            # await self._import_amo_leads(
            #     client=client, agent=agent, active_project=payload.active_project, leads=contact_leads
            # )
            not_created_projects: list[Project] = await self._find_not_created_projects(
                client=client, agent_id=agent.id, payload=payload
            )

            return await self._create_requested_leads(
                amocrm,
                client=client,
                not_created_projects=not_created_projects,
                agent=agent,
            )

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
            leads.extend(await amocrm.fetch_leads(lead_ids=lead_ids, query_with=[AmoLeadQueryWith.contacts]))
        return leads

    async def _import_amo_leads(
        self, client: User, agent: User, active_project: int, leads: list[AmoLead]
    ) -> None:
        """
        Импортируем сделки из Амо.
        Тут импортируются только активные сделки пользователя из амо для проектов,
        которые переданы в active_project.
        @param active_project: int. ЖК/Проект из запроса.
        @param client: User
        @param leads: list[AmoLead]. Список сделок клиента из амо.
        """
        queryset = self.project_repo.list()
        active_pipeline_ids: list[str] = await self.project_repo.facets(
            field='amo_pipeline_id', queryset=queryset, filters=dict(id=active_project)
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
                    filters=dict(amo_pipeline_id=lead.pipeline_id, amocrm_name=amocrm_name[0])
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
            else:
                booking_source: BookingSource = await get_booking_source(slug=BookingCreatedSources.AMOCRM)
                data.update(
                    amocrm_id=lead.id,
                    created_source=BookingCreatedSources.AMOCRM,  # todo: deprecated
                    booking_source=booking_source,
                )
                booking = await self.booking_create(data=data)

            await self._create_task_instance([booking.id])

    async def _find_not_created_projects(
        self,
        client: User,
        agent_id: int,
        payload: RequestAssignClient,
    ) -> list[Project]:
        """
        Находим не созданные в бд сделки, исходя из переданных в запросе id проектов.
        @param client: User
        @param payload: RequestAssignClient
        @return: list[Project]
        """
        # filters: dict[str, Any] = dict(active=True, user_id=client.id, agent_id=agent_id)
        # bookings: list[Booking] = await self.booking_repo.list(filters=filters)
        # booking_projects: set = {booking.project_id for booking in bookings}
        # not_created_project_ids = {payload.active_project}.difference(booking_projects)

        return await self.project_repo.list(
            filters=dict(id__in=[payload.active_project]),
            related_fields=["city"]
        )

    async def _create_requested_leads(
        self,
        amocrm: AmoCRM,
        client: User,
        not_created_projects: list[Project],
        agent: User,
    ) -> Booking:
        """
        Создаём сделки в амо в тех воронках, которые переданы в запросе, если таких сделок ещё нет.
        Создаём так-же в бд.
        @param client: User
        @param not_created_projects: list[Project]
        """
        status_name: str = 'фиксация клиента за ан'
        tags: list[str] = self.lk_broker_tag + self.lk_test_tag if client.is_test_user else self.lk_broker_tag
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
                tags=tags,
                # is_agency_deal=True,
            )
            print(f"New lead AMO data: {amo_data}")
            lead: list[AmoLead] = await amocrm.create_lead(**amo_data)
            booking_source: BookingSource = await get_booking_source(slug=BookingCreatedSources.LK_ASSIGN)
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
                created_source=BookingCreatedSources.LK_ASSIGN,  # todo: deprecated
                booking_source=booking_source,
                tags=tags,
                active=True,
            )
            booking = await self.booking_repo.retrieve(filters=dict(amocrm_id=lead_amocrm_id))
            if booking:
                booking = await self.booking_update(booking=booking, data=data)
            else:
                booking = await self.booking_create(data=data)

            await booking.refresh_from_db(fields=["id"])
            await self._create_task_instance(booking.id, booking_created=True)
            self.check_pinning.as_task(user_id=client.id)

            return booking

    async def _get_status_by_name(self, name: str, pipeline_id: Union[str, int]) -> Optional[AmocrmStatus]:
        """
        @param pipeline_id: int. ID воронки
        @return: Optional[AmocrmStatus]
        """
        filters = dict(name__icontains=name, pipeline_id=pipeline_id)
        status: Optional[AmocrmStatus] = await self.amo_statuses_repo.retrieve(filters=filters)
        return status

    async def _create_task_instance(self, booking_id: int, booking_created: bool = False) -> None:
        """
        Создаем задачу на создание экземпляра задачи.
        @param booking_id: int
        """
        await self.create_task_instance_service(booking_ids=booking_id,  booking_created=booking_created)
