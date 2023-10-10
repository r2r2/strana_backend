from typing import Any, Optional, Type

from common.amocrm.types import AmoLead
from config import EnvTypes, maintenance_settings
from src.agreements.repos import AgencyAgreement, AgreementType
from src.booking.repos import Booking
from src.getdoc.repos import DocTemplate
from src.projects.repos import Project
from src.users.repos import User
from .. import exceptions
from ..entities import BaseAgencyCase
from ..repos import Agency, AgencyRepo
from ..types import (AgencyAgreementRepo, AgencyAgreementTypeRepo,
                     AgencyAmoCRM, AgencyBookingRepo, AgencyDocTemplateRepo,
                     AgencyProjectRepo,
                     AgencyUserRepo)


class RepresAgenciesCreateAgreementCase(BaseAgencyCase):
    """
    Создание договора агентства
    """

    lk_broker_tag: list[str] = ["ЛК Брокера"]
    dev_test_booking_tag: list[str] = ['Тестовая бронь']
    stage_test_booking_tag: list[str] = ['Тестовая бронь Stage']

    def __init__(
        self,
        booking_getdoc_statuses: Any,
        agency_repo: Type[AgencyRepo],
        user_repo: Type[AgencyUserRepo],
        amocrm_class: Type[AgencyAmoCRM],
        project_repo: Type[AgencyProjectRepo],
        agreement_repo: Type[AgencyAgreementRepo],
        agreement_type_repo: Type[AgencyAgreementTypeRepo],
        booking_repo: Type[AgencyBookingRepo],
        doc_template_repo: Type[AgencyDocTemplateRepo],
    ) -> None:
        self._booking_getdoc_statuses: Any = booking_getdoc_statuses
        self._agency_repo: AgencyRepo = agency_repo()
        self._user_repo: AgencyUserRepo = user_repo()
        self._project_repo: AgencyProjectRepo = project_repo()
        self._agreement_repo: AgencyAgreementRepo = agreement_repo()
        self._booking_repo: AgencyBookingRepo = booking_repo()
        self._agreement_type_repo: AgencyAgreementTypeRepo = agreement_type_repo()
        self._doc_template_repo: AgencyDocTemplateRepo = doc_template_repo()
        self._amocrm_class: Type[AgencyAmoCRM] = amocrm_class

    async def __call__(self, *, repres_id: int, projects_ids: list[int], type_id: int) -> list[AgencyAgreement]:
        agency: Optional[Agency] = await self._agency_repo.retrieve(filters=dict(maintainer=repres_id))
        if not agency:
            raise exceptions.AgencyNotFoundError

        repres: User = await self._user_repo.retrieve(filters=dict(id=repres_id))

        agreement_type: Optional[AgreementType] = await self._agreement_type_repo.retrieve(filters=dict(id=type_id))
        if not agreement_type:
            raise exceptions.AgencyAgreementTypeNotExists

        projects: list[Project] = await self._project_repo.list(filters=dict(id__in=projects_ids))
        if len(projects) == 0:
            raise exceptions.AgencyProjectNotFoundError

        agreements = []

        for project in projects:
            filters = dict(project_id=project.id, type=agency.type.value, agreement_type_id=agreement_type.id)
            doc_templates: list[DocTemplate] = await self._doc_template_repo.list(filters=filters)
            if len(doc_templates) == 0:
                continue

            for template in doc_templates:
                booking: Booking = await self._create_agreement_lead(agency, repres, project)
                agreement: AgencyAgreement = await self._create_agreement(
                    repres=repres,
                    booking=booking,
                    agency=agency,
                    project=project,
                    agreement_type=agreement_type,
                    template_name=template.template_name,
                )
                agreements.append(agreement)
        return agreements

    async def _create_agreement_lead(self, agency: Agency, repres: User, project: Project) -> Booking:
        """
        Создание сделки для получения договора
        """
        tags = self.lk_broker_tag
        if maintenance_settings["environment"] == EnvTypes.DEV:
            tags = tags + self.dev_test_booking_tag
        elif maintenance_settings["environment"] == EnvTypes.STAGE:
            tags = tags + self.stage_test_booking_tag

        lead_options: dict[str, Any] = dict(
            status_id=self._booking_getdoc_statuses.NEW,
            city_slug=self._amocrm_class.city_name_mapping.get(agency.city, "tyumen"),
            user_amocrm_id=repres.amocrm_id,
            project_amocrm_name=project.amocrm_name,
            project_amocrm_enum=project.amocrm_enum,
            project_amocrm_pipeline_id=project.amo_pipeline_id,
            project_amocrm_responsible_user_id=project.amo_responsible_user_id,
            companies=[agency.amocrm_id],
            creator_user_id=repres.id,
            tags=tags,
        )
        async with await self._amocrm_class() as amocrm:
            data: list[AmoLead] = await amocrm.create_lead(**lead_options)

        booking_data = dict(
            project_id=project.id,
            amocrm_id=data[0].id,
            user_id=repres.id,
            active=True
        )
        return await self._booking_repo.create(booking_data)

    async def _create_agreement(
        self,
        *,
        repres: User,
        booking: Booking,
        agency: Agency,
        project: Project,
        agreement_type: AgreementType,
        template_name: str,
    ) -> AgencyAgreement:
        """Получение договора для агентства"""
        agreement_data = dict(
            agency_id=agency.id,
            booking_id=booking.id,
            project_id=project.id,
            agreement_type_id=agreement_type.id,
            template_name=template_name,
            created_by=repres,
        )
        agreement: AgencyAgreement = await self._agreement_repo.create(data=agreement_data)
        select_related = ["status", "agreement_type", "agency"]
        return await self._agreement_repo.retrieve(filters=dict(id=agreement.id), related_fields=select_related)
