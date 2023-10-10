from typing import Any, Type

from common.amocrm.types import AmoLead
from common.getdoc.types import project_filename_mapping
from config import EnvTypes, maintenance_settings
from fastapi import UploadFile
from src.projects.repos import Project
from src.users.repos import User

from ..constants import FileType, UploadPath
from ..entities import BaseAgencyCase
from ..exceptions import AgencyProjectNotFoundError
from ..repos import Agency, AgencyRepo
from ..types import (AgencyAmoCRM, AgencyFileProcessor, AgencyGetDoc,
                     AgencyProjectRepo, AgencyUserRepo)
from ..loggers.wrappers import agency_changes_logger


class RepresAgenciesFileCase(BaseAgencyCase):
    """
    Получение договора агентства
    """

    lk_broker_tag: list[str] = ["ЛК Брокера"]
    dev_test_booking_tag: list[str] = ['Тестовая бронь']
    stage_test_booking_tag: list[str] = ['Тестовая бронь Stage']

    def __init__(
        self,
        booking_substages: Any,
        agency_repo: Type[AgencyRepo],
        user_repo: Type[AgencyUserRepo],
        file_processor: Type[AgencyFileProcessor],
        getdoc_class: Type[AgencyGetDoc],
        amocrm_class: Type[AgencyAmoCRM],
        project_repo: Type[AgencyProjectRepo],
    ) -> None:
        self._booking_substages: Any = booking_substages
        self._agency_repo: AgencyRepo = agency_repo()
        self.agency_update = agency_changes_logger(
            self._agency_repo.update, self, content="Обновление данных агентства"
        )
        self._user_repo: AgencyUserRepo = user_repo()
        self._project_repo: AgencyProjectRepo = project_repo()
        self._file_processor: Type[AgencyFileProcessor] = file_processor
        self._getdoc_class: Type[AgencyGetDoc] = getdoc_class
        self._amocrm_class: Type[AgencyAmoCRM] = amocrm_class

    async def __call__(self, repres_id: int, project_id: int):
        agency: Agency = await self._agency_repo.retrieve(filters=dict(maintainer=repres_id))
        repres: User = await self._user_repo.retrieve(filters=dict(id=repres_id))
        project: Project = await self._project_repo.retrieve(filters=dict(id=project_id))
        if not agency.getdoc_lead_id:
            agency = await self._create_getdoc_lead(agency, repres, project)

        file: UploadFile = await self._get_doc(agency, project)
        agreement_files = await self._file_processor(
            files=dict(agreement_files=[file]),
            path=UploadPath.FILES,
            choice_class=FileType,
        )
        agency_files = agency.files
        agency_files.append(agreement_files[0])
        agency = await self.agency_update(agency, data=dict(files=agency_files))
        return agency

    async def _create_getdoc_lead(self, agency: Agency, repres: User, project: Project) -> Agency:
        """
        Создание сделки для получения договора
        """
        tags = self.lk_broker_tag
        if maintenance_settings["environment"] == EnvTypes.DEV:
            tags = tags + self.dev_test_booking_tag
        elif maintenance_settings["environment"] == EnvTypes.STAGE:
            tags = tags + self.stage_test_booking_tag

        lead_options: dict[str, Any] = dict(
            status=self._booking_substages.ASSIGN_AGENT,
            city_slug=self._amocrm_class.city_name_mapping.get(agency.city, "tyumen"),
            user_amocrm_id=repres.amocrm_id,
            project_amocrm_name=project.amocrm_name,
            project_amocrm_enum=project.amocrm_enum,
            project_amocrm_pipeline_id=project.amo_pipeline_id,
            project_amocrm_responsible_user_id=project.amo_responsible_user_id,
            creator_user_id=repres.id,
            tags=tags,
        )
        async with self._amocrm_class() as amocrm:
            data: list[AmoLead] = await amocrm.create_lead(**lead_options)
        lead_id: int = data[0].id
        return await self.agency_update(agency, data=dict(getdoc_lead_id=lead_id))

    async def _get_doc(self, agency: Agency, project: Project) -> UploadFile:
        """Получение дговора для агенства"""
        async with self._getdoc_class() as getdoc:
            filename = None
            templates = project_filename_mapping.get(project.amo_pipeline_id)
            if templates:
                filename = templates.get(agency.type)
            if not filename:
                raise AgencyProjectNotFoundError
            file: UploadFile = await getdoc.get_doc(agency.getdoc_lead_id, filename)
        return file
