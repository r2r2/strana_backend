from copy import copy
from typing import Any, Optional, Type, Union

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
        agencies: list[Agency] = await self.agency_repo.list(filters=filters).only('id', 'inn').values_list('id', 'inn')

        for agency_id, agency_inn in agencies:
            async with await self.amocrm_class() as amocrm:
                amocrm_companies: list[AmoCompany] = await amocrm.fetch_companies(agency_inn=agency_inn)
                if amocrm_companies:
                    agency: Agency = await self.agency_repo.retrieve(
                        filters={"id": agency_id, "amocrm_id__isnull": True}, prefetch_fields=['maintainer']
                    )
                    data: dict[str, str] = {'amocrm_id': amocrm_companies[0]['id']}
                    await self.agency_repo.update(model=agency, data=data)
                    try:
                        await self.agency_repo.update(model=agency, data=data)
                    except ValidationError as err:
                        raise AgencyInvalidFillDataError from err
