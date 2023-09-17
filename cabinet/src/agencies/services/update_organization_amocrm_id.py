from copy import copy
from typing import Any, Optional, Type, Union

from common.amocrm.components import AmoCRMCompanies
from common.amocrm.types import AmoCompany

from ..entities import BaseAgencyService
from ..exceptions import AgencyInvalidFillDataError
from ..repos import Agency, AgencyRepo
from ..types import AgencyAmoCRM, AgencyORM
from tortoise.exceptions import ValidationError


class UpdateOrganizationAmocrmIdService(BaseAgencyService):
    """
    Обновление amocrm_id в организации
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

    async def __call__(self) -> None:
        filters: dict[str, Any] = dict(amocrm_id__isnull=True)
        agencies: list[Agency] = await self.agency_repo.list(filters=filters)
        filter_custom_field = dict(
            field_id=AmoCRMCompanies.inn_field_id,
            values=[agency.inn for agency in agencies]
        )

        async with await self.amocrm_class() as amocrm:
            amocrm_companies: list[AmoCompany] = await amocrm.fetch_companies(filter_custom_field=filter_custom_field)
            if amocrm_companies:
                data_for_update = {field.values[0].value: amocrm_company.id
                                   for amocrm_company in amocrm_companies
                                   for field in amocrm_company.custom_fields_values
                                   if field.field_id == AmoCRMCompanies.inn_field_id}

                for agency in agencies:
                    if str(agency.inn) in data_for_update:
                        data: dict[str, int] = {'amocrm_id': data_for_update[str(agency.inn)]}
                        try:
                            await self.agency_repo.update(model=agency, data=data)
                        except ValidationError as err:
                            raise AgencyInvalidFillDataError from err
