from ..entities import BasePrivilegeServiceCase
from ..repos import PrivilegeInfoRepo, PrivilegeInfo


class InfoListCase(BasePrivilegeServiceCase):
    """
    Кейс получения Общей информации
    """

    def __init__(
        self,
        info_repo: type[PrivilegeInfoRepo],
    ) -> None:
        self.info_repo: PrivilegeInfoRepo = info_repo()

    async def __call__(self) -> list[PrivilegeInfo]:
        info: list[PrivilegeInfo] = await self.info_repo.list()
        return info
