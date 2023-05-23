from copy import copy
from typing import Any, Optional, Type, Union

from common.amocrm.components import CompanyUpdateParams

from ..entities import BaseAgencyService
from ..repos import Agency, AgencyRepo
from ..types import AgencyAmoCRM, AgencyORM


class UpdateOrganizationService(BaseAgencyService):
    """
    Обновление организации в AmoCRM
    """

    def __init__(
        self,
        agency_repo: Type[AgencyRepo],
        amocrm_class: Type[AgencyAmoCRM],
        orm_class: Optional[Type[AgencyORM]] = None,
        orm_config: Optional[dict[str, Any]] = None,
    ) -> None:
        self.agency_repo: AgencyRepo = agency_repo()
        self.amocrm_class: Type[AgencyAmoCRM] = amocrm_class

        self.orm_class: Union[Type[AgencyORM], None] = orm_class
        self.orm_config: Union[dict[str, Any], None] = copy(orm_config)
        if self.orm_config:
            self.orm_config.pop("generate_schemas", None)

    async def __call__(
        self,
        agency_id: Optional[int] = None,
    ) -> None:
        filters: dict[str, Any] = dict(id=agency_id)
        agency: Agency = await self.agency_repo.retrieve(filters=filters)

        if agency and agency.amocrm_id:
            async with await self.amocrm_class() as amocrm:
                await self._update_company_data(agency, amocrm)

    @staticmethod
    async def _update_company_data(agency: Agency, amocrm: AgencyAmoCRM):
        """
        Обновление данных компании
        """
        signatory_fio = None
        if all((agency.signatory_name, agency.signatory_surname)):
            signatory_fio = f"{agency.signatory_surname} {agency.signatory_name} {agency.signatory_patronymic}"

        company_update = CompanyUpdateParams(
            agency_id=agency.amocrm_id,
            agency_name=agency.name,
            agency_inn=agency.inn,
            agency_tags=agency.tags,
            state_registration_number=agency.state_registration_number,
            legal_address=agency.legal_address,
            bank_name=agency.bank_name,
            bank_identification_code=agency.bank_identification_code,
            checking_account=agency.checking_account,
            correspondent_account=agency.correspondent_account,
            signatory_name=agency.signatory_name,
            signatory_surname=agency.signatory_surname,
            signatory_patronymic=agency.signatory_patronymic,
            signatory_fio=signatory_fio,
            signatory_registry_number=agency.signatory_registry_number,
            signatory_sign_date=agency.signatory_sign_date,
        )
        await amocrm.update_company(company_update)
