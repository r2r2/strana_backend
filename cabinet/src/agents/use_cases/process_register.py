import asyncio
from asyncio import Task
from secrets import token_urlsafe
from typing import Type, Any, Callable, Optional

import structlog

from src.users.constants import UserType
from celery.local import PromiseProxy

from ..repos import AgentRepo, User
from ..entities import BaseAgentCase
from ..models import RequestProcessRegisterModel
from ..exceptions import AgentNoAgencyError
from ..types import AgentEmail, AgentHasher, AgentAgencyRepo
from ..services import CreateContactService, EnsureBrokerTagService
from ...agencies.repos import Agency
from src.users.loggers.wrappers import user_changes_logger
from src.users.services import UserCheckUniqueService


class ProcessRegisterCase(BaseAgentCase):
    """
    Регистрация
    """

    agent_confirm_template: str = "src/agents/templates/confirm_email.html"
    repres_notice_template: str = "src/agents/templates/repres_notify.html"
    confirm_link: str = "https://{}/confirm/agents/confirm_email?q={}&p={}"
    broker_link: str = "https://{}"

    def __init__(
        self,
        user_type: str,
        agent_repo: Type[AgentRepo],
        site_config: dict[str, Any],
        email_class: Type[AgentEmail],
        hasher: Callable[..., AgentHasher],
        agency_repo: Type[AgentAgencyRepo],
        token_creator: Callable[[int], str],
        import_clients_task: PromiseProxy,
        bind_contact_company_task: PromiseProxy,
        create_contact_service: CreateContactService,
        ensure_broker_tag_service: EnsureBrokerTagService,
        check_user_unique_service: UserCheckUniqueService,
        logger=structlog.getLogger(__name__),
    ) -> None:
        self.hasher: AgentHasher = hasher()
        self.agent_repo: AgentRepo = agent_repo()
        self.agent_create = user_changes_logger(
            self.agent_repo.create, self, content="Создание агента"
        )
        self.agent_delete = user_changes_logger(
            self.agent_repo.delete, self, content="Удаление агента"
        )
        self.agency_repo: AgentAgencyRepo = agency_repo()
        self.import_clients_task: PromiseProxy = import_clients_task
        self.bind_contact_company_task: PromiseProxy = bind_contact_company_task

        self.create_contact_service: CreateContactService = create_contact_service
        self.ensure_broker_tag_service: EnsureBrokerTagService = ensure_broker_tag_service
        self.check_user_unique_service: UserCheckUniqueService = check_user_unique_service

        self.user_type: str = user_type
        self.email_class: Type[AgentEmail] = email_class
        self.token_creator: Callable[[int], str] = token_creator

        self.site_host: str = site_config["site_host"]
        self.broker_site_host: str = site_config["broker_site_host"]
        self.logger = logger

    async def __call__(self, payload: RequestProcessRegisterModel) -> User:
        data: dict[str, Any] = payload.dict()

        agency_id: int = data.pop("agency")
        filters: dict[str, Any] = dict(id=agency_id, is_approved=True)
        agency: Agency = await self.agency_repo.retrieve(
            filters=filters, prefetch_fields=['maintainer'])
        if not agency:
            raise AgentNoAgencyError
        data["agency_id"]: int = agency_id

        email: str = data["email"]
        phone: str = data["phone"]
        password: str = data.pop("password_1")

        # Удаляем запись помеченного удалённым агента из БД,
        # если есть такой с указанным телефоном или мылом
        filters = dict(type=UserType.AGENT, is_deleted=True)
        q_filters = [
            self.agent_repo.q_builder(or_filters=[dict(phone=phone), dict(email__iexact=email)])
        ]
        deleted_agent = await self.agent_repo.retrieve(filters=filters, q_filters=q_filters)
        if deleted_agent is not None:
            await self.agent_delete(deleted_agent)
        await self.check_user_unique_service(payload)

        extra_data: dict[str, Any] = dict(
            duty_type=None,
            type=self.user_type,
            email_token=token_urlsafe(32),
            password=self.hasher.hash(password),
            is_active=True,
            is_approved=True,
        )
        data.update(extra_data)
        agent: User = await self.agent_create(data=data)
        await self._import_contacts(agent=agent, agency=agency)
        token = self.token_creator(agent.id)
        await asyncio.gather(
            self._send_confirm_email(agent=agent, token=token),
            self._send_agency_email(agent=agent, agency=agency)
        )
        return agent

    async def _send_confirm_email(self, agent: User, token: str) -> Task:
        confirm_link: str = self.confirm_link.format(self.site_host, token, agent.email_token)
        email_options: dict[str, Any] = dict(
            topic="Подтверждение почты",
            template=self.agent_confirm_template,
            recipients=[agent.email],
            context=dict(confirm_link=confirm_link),
        )
        email_service: AgentEmail = self.email_class(**email_options)
        return email_service.as_task()

    async def _send_agency_email(self, agency: Agency, agent: User) -> Optional[Task]:
        if not agency.maintainer:
            self.logger.warning(f'Agency without maintainer: id<{agency.id}>')
            return
        context: dict[str: Any] = dict(
            url=self.broker_link.format(self.broker_site_host),
            agent=agent,
            agency=agency
        )
        email_options: dict[str: Agency] = dict(
            topic='В сервис кабинет брокера добавлен сотрудник',
            template=self.repres_notice_template,
            recipients=[agency.maintainer.email],
            context=context
        )
        email_service: AgentEmail = self.email_class(**email_options)
        return email_service.as_task()

    async def _import_contacts(self, agent: User, agency: Agency):
        amocrm_id, tags = await self.create_contact_service(agent=agent)
        setattr(agent, "tags", tags)
        await self.ensure_broker_tag_service(agent=agent)
        self.import_clients_task.delay(agent_id=agent.id)
        self.bind_contact_company_task.delay(
            agent_amocrm_id=amocrm_id, agency_amocrm_id=agency.amocrm_id)
