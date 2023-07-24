import asyncio
from typing import Type, Optional

from common.amocrm import AmoCRM
from common.amocrm.components import CompanyUpdateParams
from common.files import FileProcessor
from src.agencies.entities import BaseAgencyCase
from src.agencies.exceptions import RepresAgencyNotFoundError
from src.agencies.constants import FileType as AgencyFileType, UploadPath as AgencyUploadPath
from src.agencies.models import RequestUpdateProfile
from src.agencies.repos import AgencyRepo, Agency
from src.represes.repos import RepresRepo
from src.users.repos import User
from ..loggers.wrappers import agency_changes_logger


class UpdateAgencyProfile(BaseAgencyCase):
    """
    Обновление данных текстовых и файловых данных профиля агентства
    """
    def __init__(
        self,
        repres_repo: Type[RepresRepo],
        agency_repo: Type[AgencyRepo],
        file_processor: Type[FileProcessor],
        amocrm_class: Type[AmoCRM]
    ):
        self.repres_repo = repres_repo()
        self.agency_repo = agency_repo()
        self.agency_update = agency_changes_logger(
            self.agency_repo.update, self, content="Обновление данных профиля агентства"
        )
        self.agency_files_update = agency_changes_logger(
            self.agency_repo.update_files, self, content="Обновление файловых данных агентства"
        )
        self.file_processor: Type[FileProcessor] = file_processor
        self.amocrm_class = amocrm_class

    async def __call__(
            self,
            repres_id: int,
            payload: RequestUpdateProfile,
            **files
    ):
        filters = dict(id=repres_id)
        repres: User = await self.repres_repo.retrieve(
            filters=filters,
            prefetch_fields=["maintained"]
        )
        agency: Agency = repres.maintained
        if not agency:
            raise RepresAgencyNotFoundError

        data: dict = payload.dict(exclude_unset=True, exclude_none=True)
        await agency.fetch_related("city")

        agency = await self._proceed_agency_changes(agency, data, **files)
        await asyncio.gather(
            self._update_amo_info(agency, payload)
        )
        return agency

    async def _update_amo_info(self, agency: Agency, payload: RequestUpdateProfile) -> None:
        """Invoke amo API"""
        agency_update_data = CompanyUpdateParams(
            agency_id=agency.amocrm_id,
            agency_name=payload.name
        )
        async with await self.amocrm_class() as amocrm:
            await amocrm.update_company(
                agency_update_data
            )

    async def _proceed_agency_changes(
            self,
            agency: Agency,
            json_data: Optional[dict],
            **files
    ) -> Agency:
        """
        Invoke agency file update and usual update
        """
        if len(json_data) != 0:
            agency = await self.agency_update(agency, data=json_data)
        if len(files) != 0:
            precessed_data = await self.file_processor(
                files=files,
                path=AgencyUploadPath.FILES,
                choice_class=AgencyFileType
            )
            agency = await self.agency_files_update(agency, data=precessed_data)
        return agency
