from typing import Any, Type, Optional

from common.amocrm.types import AmoLead
from config import EnvTypes, maintenance_settings
from fastapi import UploadFile
from src.agreements.constants import AdditionalAgreementFileType
from src.agreements.repos import AgencyAdditionalAgreement
from src.booking.repos import Booking, TestBookingRepo
from src.projects.repos import Project
from src.users.repos import User
from src.agents.repos import AgentRepo

from ..constants import UploadPath
from ..entities import BaseAgencyCase
from ..repos import Agency, AgencyRepo
from ..exceptions import AdditionalAgreementNotExists, AgencyMainteinerNotExists
from ..types import (AgencyAmoCRM, AgencyBookingRepo,
                     AgencyFileProcessor, AgencyGetDoc,
                     AgencyAdditionalAgreementRepo, AgencyAdminsRepo)


class AgenciesAdditionalAgreementGetDocCase(BaseAgencyCase):
    """
    Формирование документа для скачивания из get_doc
    """
    lk_broker_tag: list[str] = ["ЛК Брокера"]
    dev_test_booking_tag: list[str] = ['Тестовая бронь']
    stage_test_booking_tag: list[str] = ['Тестовая бронь Stage']

    def __init__(
        self,
        admin_repo: Type[AgencyAdminsRepo],
        booking_getdoc_statuses: Any,
        agency_repo: Type[AgencyRepo],
        file_processor: Type[AgencyFileProcessor],
        getdoc_class: Type[AgencyGetDoc],
        amocrm_class: Type[AgencyAmoCRM],
        booking_repo: Type[AgencyBookingRepo],
        additional_agreement_repo: Type[AgencyAdditionalAgreementRepo],
        agent_repo: Type[AgentRepo],
        test_booking_repo: Type[TestBookingRepo],
    ) -> None:
        self._admin_repo: Type[AgencyAdminsRepo] = admin_repo()
        self._booking_getdoc_statuses: Any = booking_getdoc_statuses
        self._agency_repo: AgencyRepo = agency_repo()
        self._booking_repo: AgencyBookingRepo = booking_repo()
        self._file_processor: Type[AgencyFileProcessor] = file_processor
        self._getdoc_class: Type[AgencyGetDoc] = getdoc_class
        self._amocrm_class: Type[AgencyAmoCRM] = amocrm_class
        self._additional_agreement_repo: Type[AgencyAdditionalAgreementRepo] = additional_agreement_repo()
        self._agent_repo: AgentRepo = agent_repo()
        self._test_booking_repo: TestBookingRepo = test_booking_repo()

    async def __call__(
        self,
        *,
        additional_id: int,
        repres_id: Optional[int] = None,
        admin_id: Optional[int] = None,
        agent_id: Optional[int] = None,
    ) -> AgencyAdditionalAgreement:
        additional_agreement: AgencyAdditionalAgreement = await self._additional_agreement_repo.retrieve(
            filters=dict(id=additional_id),
            related_fields=["status", "agency", "agency__maintainer", "project"],
        )

        if repres_id and additional_agreement.agency.maintainer.id != int(repres_id):
            raise AdditionalAgreementNotExists

        agency = additional_agreement.agency
        project = additional_agreement.project

        if agent_id:
            agent = await self._agent_repo.retrieve(filters=dict(id=agent_id))
            if agent.agency_id != agency.id:
                raise AdditionalAgreementNotExists

        if not agency.maintainer:
            raise AgencyMainteinerNotExists

        if additional_agreement.files:
            return additional_agreement

        booking: Booking = await self._create_additional_agreement_lead(
            agency=agency,
            lead_user=agency.maintainer,
            project=project
        )
        if agent_id:
            is_test_user = agent.is_test_user
        else:
            is_test_user = agency.maintainer.is_test_user
        data: dict[str, Any] = dict(
            booking=booking,
            amocrm_id=booking.amocrm_id,
            is_test_user=is_test_user,
        )
        await self._test_booking_repo.create(data=data)

        additional_agreement: AgencyAdditionalAgreement = await self._additional_agreement_get_document(
            additional_agreement=additional_agreement,
            booking=booking
        )

        return additional_agreement

    async def _create_additional_agreement_lead(self, agency: Agency, lead_user: User, project: Project) -> Booking:
        """
        Создание сделки для формирования документа в get_doc
        """
        tags = self.lk_broker_tag
        if maintenance_settings["environment"] == EnvTypes.DEV:
            tags = tags + self.dev_test_booking_tag
        elif maintenance_settings["environment"] == EnvTypes.STAGE:
            tags = tags + self.stage_test_booking_tag

        lead_options: dict[str, Any] = dict(
            status_id=self._booking_getdoc_statuses.NEW,
            city_slug=self._amocrm_class.city_name_mapping.get(agency.city, "tmn"),
            user_amocrm_id=lead_user.amocrm_id,
            project_amocrm_name=project.amocrm_name,
            project_amocrm_enum=project.amocrm_enum,
            project_amocrm_pipeline_id=project.amo_pipeline_id,
            project_amocrm_responsible_user_id=project.amo_responsible_user_id,
            companies=[agency.amocrm_id],
            creator_user_id=lead_user.id,
            tags=tags,
        )
        async with await self._amocrm_class() as amocrm:
            data: list[AmoLead] = await amocrm.create_lead(**lead_options)

        booking_data = dict(
            project_id=project.id,
            amocrm_id=data[0].id,
            user_id=lead_user.id,
            active=True
        )

        return await self._booking_repo.create(booking_data)

    async def _additional_agreement_get_document(
        self,
        *,
        additional_agreement: AgencyAdditionalAgreement,
        booking: Booking,
    ) -> AgencyAdditionalAgreement:
        """Получение файла документа дополнительного соглашения из get_doc"""

        async with await self._getdoc_class() as getdoc:
            file: UploadFile = await getdoc.get_doc(
                booking.amocrm_id,
                additional_agreement.template_name
            )
        agreement_files = await self._file_processor(
            files=dict(additional_agreement_file=[file]),
            path=UploadPath.FILES,
            choice_class=AdditionalAgreementFileType,
        )
        agreement_data = dict(
            booking_id=booking.id,
            files=agreement_files,
        )

        return await self._additional_agreement_repo.update(additional_agreement, data=agreement_data)
