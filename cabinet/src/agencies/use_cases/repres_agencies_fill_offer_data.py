from typing import Any, Optional, Type

from src.users.repos import User
from tortoise.exceptions import ValidationError

from ..entities import BaseAgencyCase
from ..exceptions import AgencyInvalidFillDataError, AgencyNotFoundError
from ..loggers.wrappers import agency_changes_logger
from ..models import RequestRepresAgenciesFillOfferModel
from ..repos import Agency, AgencyRepo
from ..types import AgencyUserRepo


class AgenciesFillOfferCase(BaseAgencyCase):
    """
    Заполнение данных договора агентства представителем
    """

    def __init__(
        self,
        agency_repo: Type[AgencyRepo],
        update_company_service: Any,
        user_repo: Type[AgencyUserRepo],
    ) -> None:
        self.agency_repo: AgencyRepo = agency_repo()
        self.agency_update = agency_changes_logger(
            self.agency_repo.update, self, content="Обновление данных договора агентства"
        )
        self.user_repo: AgencyUserRepo = user_repo()

        self.update_company_service: Any = update_company_service

    async def __call__(
        self,
        payload: RequestRepresAgenciesFillOfferModel,
        repres_id: Optional[int] = None,
        agent_id: Optional[int] = None,
    ) -> Agency:
        data: dict[str, Any] = payload.dict(exclude_unset=True, exclude_none=True)
        if repres_id:
            agency: Agency = await self.agency_repo.retrieve(filters=dict(maintainer=repres_id))
        else:
            agent: User = await self.user_repo.retrieve(filters=dict(id=agent_id), related_fields=["agency"])
            agency: Agency = await agent.agency

        if not agency:
            raise AgencyNotFoundError

        if len(payload.state_registration_number) == 13:
            data.update(dict(type="OOO"))
        else:
            data.update(dict(type="IP"))

        try:
            agency: Agency = await self.agency_update(agency=agency, data=data)
        except ValidationError as err:
            raise AgencyInvalidFillDataError from err

        await self.update_company_service(agency_id=agency.id)
        return agency
