import structlog
from asyncio import Task
from typing import Any, Optional, Type

from celery.local import PromiseProxy
from src.agencies.exceptions import AgencyNotApprovedError, AgencyNotFoundError
from src.users.constants import UserType
from src.users.loggers.wrappers import user_changes_logger
from src.notifications.services import GetEmailTemplateService
from src.agents.services import CreateContactService, EnsureBrokerTagService
from src.agents.repos import AgentRepo

from ...agencies.repos import Agency
from ..entities import BaseRepresCase
from ..exceptions import RepresHasAgencyError
from ..models import RequestSignupInAgencyModel
from ..repos import RepresRepo, User
from ..types import RepresAgencyRepo, RepresEmail


class ProcessSignupInAgency(BaseRepresCase):
    """
    Восстановление представителя как агента в новом агентстве.
    """

    mail_event_slug = "repres_notify_email"
    broker_link: str = "https://{}"

    def __init__(
        self,
        agent_repo: Type[AgentRepo],
        repres_repo: Type[RepresRepo],
        email_class: Type[RepresEmail],
        agency_repo: Type[RepresAgencyRepo],
        bind_contact_company_task: PromiseProxy,
        create_contact_service: CreateContactService,
        ensure_broker_tag_service: EnsureBrokerTagService,
        site_config: dict[str, Any],
        get_email_template_service: GetEmailTemplateService,
        logger=structlog.getLogger(__name__),
    ) -> None:
        self.agent_repo: AgentRepo = agent_repo()
        self.repres_repo: RepresRepo = repres_repo()
        self.repres_update = user_changes_logger(
            self.repres_repo.update, self, content="Восстановление представителя как агента в новом агентстве"
        )
        self.agency_repo: RepresAgencyRepo = agency_repo()
        self.bind_contact_company_task: PromiseProxy = bind_contact_company_task
        self.create_contact_service: CreateContactService = create_contact_service
        self.ensure_broker_tag_service: EnsureBrokerTagService = ensure_broker_tag_service
        self.email_class: Type[RepresEmail] = email_class
        self.broker_site_host: str = site_config["broker_site_host"]
        self.get_email_template_service: GetEmailTemplateService = get_email_template_service
        self.logger = logger

    async def __call__(self, payload: RequestSignupInAgencyModel, repres_id: int) -> User:
        agency: Optional[Agency] = await self.agency_repo.retrieve(
            filters=dict(inn=payload.agency_inn),
            prefetch_fields=['maintainer'],
        )
        if not agency:
            raise AgencyNotFoundError
        if not agency.is_approved:
            raise AgencyNotApprovedError

        repres: User = await self.repres_repo.retrieve(filters=dict(id=repres_id))
        if repres.maintained_id or repres.agency_id:
            raise RepresHasAgencyError

        data: dict[str, Any] = dict(agency_id=agency.id, type=UserType.AGENT)
        agent = await self.repres_update(repres, data=data)

        await self._import_contacts(agent=agent, agency=agency)
        await self._send_agency_email(agent=agent, agency=agency)

        return await self.agent_repo.retrieve(filters=dict(id=agent.id), related_fields=["agency__city"])

    async def _send_agency_email(self, agency: Agency, agent: User) -> Optional[Task]:
        if not agency.maintainer:
            self.logger.warning(f'Agency without maintainer: id<{agency.id}>')
            return
        context: dict[str: Any] = dict(
            url=self.broker_link.format(self.broker_site_host),
            agent=agent,
            agency=agency
        )
        email_notification_template = await self.get_email_template_service(
            mail_event_slug=self.mail_event_slug,
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
            email_service: RepresEmail = self.email_class(**email_options)
            return email_service.as_task()

    async def _import_contacts(self, agent: User, agency: Agency):
        amocrm_id, tags = await self.create_contact_service(agent=agent)
        setattr(agent, "tags", tags)

        await self.ensure_broker_tag_service(agent=agent)

        self.bind_contact_company_task.delay(
            agent_amocrm_id=amocrm_id, agency_amocrm_id=agency.amocrm_id)
