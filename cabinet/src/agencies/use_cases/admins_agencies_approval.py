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


class AdminsAgenciesApprovalCase(BaseAgencyCase):
    """
    Одобрение агентства администратором
    """

    template = "src/agencies/templates/agency_confirmed.html"
    login_link = "https://{}/account/represes/login"

    def __init__(
        self,
        agency_repo: Type[AgencyRepo],
        repres_repo: Type[AgencyRepresRepo],
        create_contact_service: AgencyCreateContactService,
        create_organization_service: CreateOrganizationService,
        email_class: Type[AgencyEmail],
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
        email_options: dict[str, Any] = dict(
            topic="Подтверждение агентства",
            template=self.template,
            recipients=[maintainer.email],
            context=dict(login_link=login_link),
        )
        email_service: AgencyEmail = self.email_class(**email_options)
        return email_service.as_task()
