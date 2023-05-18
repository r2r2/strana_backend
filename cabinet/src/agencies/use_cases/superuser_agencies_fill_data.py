import datetime
from typing import Any, Type
import zlib

from ..entities import BaseAgencyCase
from ..exceptions import AgencyNotFoundError
from ..repos import Agency, AgencyRepo


class SuperuserAgenciesFillDataCase(BaseAgencyCase):
    """
    Обновление данные агентства в АмоСРМ после изменения в админке брокера.
    """

    def __init__(
        self,
        agency_repo: Type[AgencyRepo],
        update_company_service: Any,
    ) -> None:
        self.agency_repo: AgencyRepo = agency_repo()
        self.update_company_service: Any = update_company_service

    async def __call__(
        self,
        agency_id: int,
        data: int,
    ) -> Agency:
        agency: Agency = await self.agency_repo.retrieve(filters=dict(id=agency_id))
        if not agency:
            raise AgencyNotFoundError

        hash_date = zlib.crc32(bytes(str(datetime.datetime.now().date()), 'utf-8'))

        if agency.amocrm_id and data == hash_date:
            await self.update_company_service(agency_id=agency.id)

        return agency
