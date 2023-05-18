from typing import Type

from src.agencies.entities import BaseAgencyCase
from src.agencies.exceptions import RepresAgencyNotFoundError
from src.agencies.repos import Agency
from src.represes.repos import RepresRepo
from src.users.repos import User


class GetAgencyProfile(BaseAgencyCase):
    """Кейс получения профиля агентства по представителю"""
    def __init__(
        self,
        repres_repo: Type[RepresRepo],
    ):
        self.repres_repo = repres_repo()

    async def __call__(self, repres_id: int):
        filters = dict(id=repres_id)
        repres: User = await self.repres_repo.retrieve(
            filters=filters,
            prefetch_fields=["maintained"]
        )
        agency: Agency = repres.maintained
        if not agency:
            raise RepresAgencyNotFoundError

        return agency
