from typing import Any

from config import lk_admin_config
from ..entities import BaseAgencyCase


class SuperuserAgenciesFillDataCase(BaseAgencyCase):
    """
    Обновление данные агентства в АмоСРМ после изменения в админке брокера.
    """

    def __init__(
        self,
        export_agency_in_amo_task: Any,
    ) -> None:
        self.export_agency_in_amo_task: Any = export_agency_in_amo_task

    def __call__(
        self,
        agency_id: int,
        data: str,
    ) -> None:

        if data == lk_admin_config["admin_export_key"]:
            self.export_agency_in_amo_task.delay(agency_id=agency_id)
