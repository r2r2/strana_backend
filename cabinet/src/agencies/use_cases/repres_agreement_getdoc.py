from typing import Type, Any, Optional

from fastapi import UploadFile

from src.agencies.constants import UploadPath
from src.agencies.entities import BaseAgencyCase
from src.agencies.exceptions import AgencyAgreementNotExists, AgencyMainteinerNotExists
from src.agencies.types import AgencyGetDoc, AgencyFileProcessor
from src.agents.repos import AgentRepo
from src.agreements.constants import AgreementFileType
from src.agreements.repos import AgencyAgreementRepo, AgencyAgreement


class AgreementGetDocCase(BaseAgencyCase):
    """
    Получение договора агентства
    """
    def __init__(
        self,
        booking_getdoc_statuses: Any,
        file_processor: Type[AgencyFileProcessor],
        getdoc_class: Type[AgencyGetDoc],
        agreement_repo: Type[AgencyAgreementRepo],
        agent_repo: Type[AgentRepo],
    ):
        self._booking_getdoc_statuses: Any = booking_getdoc_statuses
        self._file_processor: Type[AgencyFileProcessor] = file_processor
        self._getdoc_class: Type[AgencyGetDoc] = getdoc_class
        self._agreement_repo: AgencyAgreementRepo = agreement_repo()
        self._agent_repo: AgentRepo = agent_repo()
        
    async def __call__(
        self,
        agreement_id: int,
        repres_id: Optional[int] = None,
        admin_id: Optional[int] = None,
        agent_id: Optional[int] = None,
    ) -> AgencyAgreement:
        agreement: AgencyAgreement = await self._agreement_repo.retrieve(
            filters=dict(id=agreement_id),
            related_fields=["status", "agency", "agency__maintainer", "booking", "agreement_type"],
        )
        
        if repres_id and agreement.agency.maintainer.id != int(repres_id):
            raise AgencyAgreementNotExists

        if agent_id:
            agent = await self._agent_repo.retrieve(filters=dict(id=agent_id))
            if agent.agency_id != agreement.agency.id:
                raise AgencyAgreementNotExists

        if not agreement.agency.maintainer:
            raise AgencyMainteinerNotExists

        if agreement.files:
            return agreement

        agreement: AgencyAgreement = await self._agreement_get_document(
            agreement=agreement,
        )
        return agreement

    async def _agreement_get_document(
        self,
        agreement: AgencyAgreement,
    ) -> AgencyAgreement:
        async with await self._getdoc_class() as getdoc:
            file: UploadFile = await getdoc.get_doc(agreement.booking.amocrm_id, agreement.template_name)

        agreement_files = await self._file_processor(
            files=dict(agreement_file=[file]),
            path=UploadPath.FILES,
            choice_class=AgreementFileType,
        )
        agreement_data = dict(
            files=agreement_files,
        )
        return await self._agreement_repo.update(agreement, data=agreement_data)
