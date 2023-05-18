from typing import Type

from ..repos import AgencyRepo
from ..entities import BaseAgencyCase


class AgencyExistsCase(BaseAgencyCase):
    """
    Проверка на наличие агентства в БД
    """

    def __init__(self, agency_repo: Type[AgencyRepo]) -> None:
        self.agency_repo: AgencyRepo = agency_repo()

    async def __call__(self, agency_inn: str) -> bool:
        filters = dict(inn=agency_inn)
        return await self.agency_repo.exists(filters=filters)
