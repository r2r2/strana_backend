import asyncio
from asyncio import Task
from typing import Any, Callable
from secrets import token_urlsafe

import structlog
from celery.local import PromiseProxy

from src.users.constants import UserType
from src.users.loggers.wrappers import user_changes_logger
from src.users.repos import UserRoleRepo
from src.users.services import UserCheckUniqueService
from src.notifications.services import GetEmailTemplateService
from src.agencies.repos import Agency
from ..repos import AgentRepo, User
from ..entities import BaseAgentCase
from ..models import RequestProcessRegisterModel
from ..exceptions import AgentNoAgencyError
from ..types import AgentEmail, AgentHasher, AgentAgencyRepo
from ..services import CreateContactService, EnsureBrokerTagService
from src.users.models import RequestUserCheckUnique
from common.schemas import UrlEncodeDTO
from common.utils import generate_notify_url


class ProcessRegisterCase(BaseAgentCase):
    """
    Регистрация
    """

    confirm_mail_event_slug: str = "agent_confirm_email"
    notify_mail_event_slug: str = "repres_notify_email"
    confirm_link_route_template: str = "/confirm/agents/confirm_email"
    broker_link: str = "https://{}"

    def __init__(
        self,
        user_type: str,
        agent_repo: type[AgentRepo],
        user_role_repo: type[UserRoleRepo],
        site_config: dict[str, Any],
        email_class: type[AgentEmail],
        hasher: Callable[..., AgentHasher],
        agency_repo: type[AgentAgencyRepo],
        token_creator: Callable[[int], str],
        import_clients_task: PromiseProxy,
        bind_contact_to_company_service: Any,
        create_contact_service: CreateContactService,
        ensure_broker_tag_service: EnsureBrokerTagService,
        get_email_template_service: GetEmailTemplateService,
        check_user_unique_service: UserCheckUniqueService,
        logger=structlog.getLogger(__name__),
    ) -> None:
        self.hasher: AgentHasher = hasher()
        self.agent_repo: AgentRepo = agent_repo()
        self.user_role_repo: UserRoleRepo = user_role_repo()
        self.agent_create = user_changes_logger(
            self.agent_repo.create, self, content="Создание агента"
        )
        self.agent_delete = user_changes_logger(
            self.agent_repo.delete, self, content="Удаление агента"
        )
        self.agency_repo: AgentAgencyRepo = agency_repo()
        self.import_clients_task: PromiseProxy = import_clients_task
        self.bind_contact_to_company_service = bind_contact_to_company_service

        self.create_contact_service: CreateContactService = create_contact_service
        self.ensure_broker_tag_service: EnsureBrokerTagService = (
            ensure_broker_tag_service
        )
        self.check_user_unique_service: UserCheckUniqueService = (
            check_user_unique_service
        )

        self.user_type: str = user_type
        self.email_class: type[AgentEmail] = email_class
        self.token_creator: Callable[[int], str] = token_creator

        self.site_host: str = site_config["site_host"]
        self.broker_site_host: str = site_config["broker_site_host"]
        self.logger = logger

        self.get_email_template_service: GetEmailTemplateService = (
            get_email_template_service
        )

    async def __call__(self, payload: RequestProcessRegisterModel) -> User:
        data: dict[str, Any] = payload.dict()

        agency_id: int = data.pop("agency")
        filters: dict[str, Any] = dict(id=agency_id, is_approved=True)
        agency: Agency = await self.agency_repo.retrieve(
            filters=filters, prefetch_fields=["maintainer"]
        )
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
            self.agent_repo.q_builder(
                or_filters=[dict(phone=phone), dict(email__iexact=email)]
            )
        ]
        deleted_agent = await self.agent_repo.retrieve(
            filters=filters, q_filters=q_filters
        )
        if deleted_agent is not None:
            await self.agent_delete(deleted_agent)
        payload: RequestUserCheckUnique = RequestUserCheckUnique(
            phone=payload.phone,
            email=payload.email,
            role=UserType.AGENT + 's',
        )
        await self.check_user_unique_service(payload)

        extra_data: dict[str, Any] = dict(
            duty_type=None,
            type=self.user_type,
            role=await self.user_role_repo.retrieve(filters=dict(slug=self.user_type)),
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
            self._send_agency_email(agent=agent, agency=agency),
        )
        return agent

    async def _send_confirm_email(self, agent: User, token: str) -> Task:
        url_data: dict[str, Any] = dict(
            host=self.site_host,
            route_template=self.confirm_link_route_template,
            query_params=dict(
                q=token,
                p=agent.email_token,
            )
        )
        url_dto: UrlEncodeDTO = UrlEncodeDTO(**url_data)
        confirm_link: str = generate_notify_url(url_dto=url_dto)
        email_notification_template = await self.get_email_template_service(
            mail_event_slug=self.confirm_mail_event_slug,
            context=dict(confirm_link=confirm_link),
        )

        if email_notification_template and email_notification_template.is_active:
            email_options: dict[str, Any] = dict(
                topic=email_notification_template.template_topic,
                content=email_notification_template.content,
                recipients=[agent.email],
                lk_type=email_notification_template.lk_type.value,
                mail_event_slug=email_notification_template.mail_event_slug,
            )
            email_service: AgentEmail = self.email_class(**email_options)
            return email_service.as_task()

    async def _send_agency_email(self, agency: Agency, agent: User) -> Task | None:
        if not agency.maintainer:
            self.logger.warning(f"Agency without maintainer: id<{agency.id}>")
            return

        context: dict[str:Any] = dict(
            url=self.broker_link.format(self.broker_site_host),
            agent=agent,
            agency=agency,
        )
        email_notification_template = await self.get_email_template_service(
            mail_event_slug=self.notify_mail_event_slug,
            context=context,
        )

        if email_notification_template and email_notification_template.is_active:
            email_options: dict[str, Any] = dict(
                topic=email_notification_template.template_topic,
                content=email_notification_template.content,
                recipients=[agency.maintainer.email],
                lk_type=email_notification_template.lk_type.value,
                mail_event_slug=email_notification_template.mail_event_slug,
            )
            email_service: AgentEmail = self.email_class(**email_options)
            return email_service.as_task()

    async def _import_contacts(self, agent: User, agency: Agency):
        amocrm_id, tags = await self.create_contact_service(agent=agent)
        setattr(agent, "tags", tags)
        await self.ensure_broker_tag_service(agent=agent)
        await self.bind_contact_to_company_service(
            agent_amocrm_id=amocrm_id,
            agency_amocrm_id=agency.amocrm_id,
        )
        self.import_clients_task.delay(agent_id=agent.id)
