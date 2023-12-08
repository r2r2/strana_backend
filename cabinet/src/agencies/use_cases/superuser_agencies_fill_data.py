from asyncio import sleep

from config import lk_admin_config
from src.agencies.services import UpdateOrganizationService
from ..entities import BaseAgencyCase


class SuperuserAgenciesFillDataCase(BaseAgencyCase):
    """
    Обновление данные агентства в АмоСРМ после изменения в админке брокера.
    """

    def __init__(
        self,
        export_agency_in_amo_service: UpdateOrganizationService,
    ) -> None:
        self.export_agency_in_amo_service: UpdateOrganizationService = export_agency_in_amo_service

    async def __call__(
        self,
        agency_id: int,
        data: str,
    ) -> None:

        if data == lk_admin_config["admin_export_key"]:
            await sleep(3)
            await self.export_agency_in_amo_service(agency_id=agency_id)
