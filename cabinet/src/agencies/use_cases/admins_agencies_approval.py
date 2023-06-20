from asyncio import Task
from typing import Type, Any

from config import site_config

from ..entities import BaseAgencyCase
from ..exceptions import AgencyNotFoundError
from ..models import RequestAdminsAgenciesApprovalModel
from ..repos import AgencyRepo, Agency
from ..services import CreateOrganizationService
from ..types import AgencyCreateContactService, AgencyEmail, AgencyRepresRepo, AgencyUser
from ..loggers.wrappers import agency_changes_logger
from src.users.loggers.wrappers import user_changes_logger
from src.notifications.services import GetEmailTemplateService


class AdminsAgenciesApprovalCase(BaseAgencyCase):
    """
    Одобрение агентства администратором
    """

    mail_event_slug = "confirm_agency"
    login_link = "https://{}/account/represes/login"

    def __init__(
        self,
        agency_repo: Type[AgencyRepo],
        repres_repo: Type[AgencyRepresRepo],
        create_contact_service: AgencyCreateContactService,
        create_organization_service: CreateOrganizationService,
        email_class: Type[AgencyEmail],
        get_email_template_service: GetEmailTemplateService,
    ) -> None:
        self.agency_repo: AgencyRepo = agency_repo()
        self.agency_update = agency_changes_logger(
            self.agency_repo.update, self, content="Подтверждение агентства"
        )
        self.repres_repo: AgencyRepresRepo = repres_repo()
        self.repres_update = user_changes_logger(
            self.repres_repo.update, self, content="Обновление агентства у представителя"
        )

        self.create_contact_service: AgencyCreateContactService = create_contact_service
        self.create_organization_service: CreateOrganizationService = create_organization_service
        self.get_email_template_service: GetEmailTemplateService = get_email_template_service

        self.email_class: Type[AgencyEmail] = email_class

    async def __call__(self, agency_id: int, payload: RequestAdminsAgenciesApprovalModel) -> Agency:
        data: dict[str, Any] = payload.dict()
        filters: dict[str, Any] = dict(id=agency_id, is_deleted=False)
        agency: Agency = await self.agency_repo.retrieve(
            filters=filters, prefetch_fields=["maintainer"]
        )
        if not agency:
            raise AgencyNotFoundError
        agency: Agency = await self.agency_update(agency=agency, data=data)
        await self.repres_update(agency.maintainer, data=data)
        if not agency.is_imported:
            await self.create_organization_service(inn=agency.inn, agency=agency)
        if not agency.maintainer.is_imported:
            await self.create_contact_service(
                phone=agency.maintainer.phone, repres=agency.maintainer
            )
        await self._send_email(agency.maintainer)
        return agency

    async def _send_email(self, maintainer: AgencyUser) -> Task:
        login_link = self.login_link.format(site_config["broker_site_host"])
        email_notification_template = await self.get_email_template_service(
            mail_event_slug=self.mail_event_slug,
            context=dict(login_link=login_link),
        )

        if email_notification_template and email_notification_template.is_active:
            email_options: dict[str, Any] = dict(
                topic=email_notification_template.template_topic,
                content=email_notification_template.content,
                recipients=[maintainer.email],
                lk_type=email_notification_template.lk_type.value,
                mail_event_slug=email_notification_template.mail_event_slug,
            )
            email_service: AgencyEmail = self.email_class(**email_options)
            return email_service.as_task()
