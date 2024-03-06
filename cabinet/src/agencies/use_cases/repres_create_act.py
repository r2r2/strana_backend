from typing import Optional, Type

from fastapi import UploadFile
from src.agreements.constants import ActFileType
from src.agreements.repos import AgencyAct, AgencyActRepo
from src.booking.repos import Booking
from src.getdoc.repos import ActTemplate
from src.users.repos import User

from .. import exceptions
from ..constants import UploadPath
from ..entities import BaseAgencyCase
from ..repos import Agency, AgencyRepo
from ..types import (AgencyActTemplateRepo, AgencyBookingRepo,
                     AgencyFileProcessor, AgencyGetDoc, AgencyUserRepo)


class CreateActCase(BaseAgencyCase):
    """
    Создание акта
    """
    def __init__(
        self,
        agency_repo: Type[AgencyRepo],
        user_repo: Type[AgencyUserRepo],
        file_processor: Type[AgencyFileProcessor],
        getdoc_class: Type[AgencyGetDoc],
        act_repo: Type[AgencyActRepo],
        booking_repo: Type[AgencyBookingRepo],
        act_template_repo: Type[AgencyActTemplateRepo],
    ) -> None:
        self._agency_repo: AgencyRepo = agency_repo()
        self._user_repo: AgencyUserRepo = user_repo()
        self._act_repo: AgencyActRepo = act_repo()
        self._booking_repo: AgencyBookingRepo = booking_repo()
        self._file_processor: Type[AgencyFileProcessor] = file_processor
        self._getdoc_class: Type[AgencyGetDoc] = getdoc_class
        self._act_template_repo: AgencyActTemplateRepo = act_template_repo()

        self.template_name: str = "Отчета-акта агентов ИП Страна Запад ГП-4 .docx"

    async def __call__(
        self,
        *,
        booking_id: int,
        repres_id: Optional[int] = None,
        agent_id: Optional[int] = None,
    ) -> AgencyAct:
        assert any((repres_id, agent_id)), "Неверные параметры"
        booking: Optional[Booking] = await self._booking_repo.retrieve(
            filters=dict(id=booking_id), prefetch_fields=["user"])
        if not booking:
            raise exceptions.AgencyBookingNotExists

        if repres_id:
            agency: Agency = await self._agency_repo.retrieve(filters=dict(maintainer=repres_id))
        else:
            agent: User = await self._user_repo.retrieve(filters=dict(id=agent_id), related_fields=["agency"])
            agency: Agency = await agent.agency
        if not agency:
            raise exceptions.AgencyNotFoundError

        user_id = agent_id or repres_id
        user: User = await self._user_repo.retrieve(filters=dict(id=user_id))

        filters = dict(project_id=booking.project_id)
        act_template: ActTemplate = await self._act_template_repo.retrieve(filters=filters)
        if act_template:
            act: AgencyAct = await self._create_act(
                user=user,
                booking=booking,
                agency=agency,
                template_name=act_template.template_name,
            )
            return act
        raise exceptions.ActTemplateNotFound

    async def _create_act(
        self,
        user: User,
        booking: Booking,
        agency: Agency,
        template_name: str,
    ) -> AgencyAct:
        """Создание акта"""
        async with await self._getdoc_class() as getdoc:
            file: UploadFile = await getdoc.get_doc(
                lead_id=booking.amocrm_id,
                contact_id=booking.user.amocrm_id,
                template=template_name,
            )

        act_files = await self._file_processor(
            files=dict(act_files=[file]),
            path=UploadPath.FILES,
            choice_class=ActFileType,
        )
        act_data = dict(
            agency_id=agency.id,
            booking_id=booking.id,
            template_name=template_name,
            files=act_files,
            created_by=user,
            project_id=booking.project_id,
        )
        act = await self._act_repo.create(data=act_data)
        select_related = ["status", "agency"]
        return await self._act_repo.retrieve(filters=dict(id=act.id), related_fields=select_related)
