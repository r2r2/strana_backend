from typing import Type, Any

from ..entities import BaseRepresCase
from ..models import RequestAcceptContractModel
from ..repos import RepresRepo, User
from ...users.loggers.wrappers import user_changes_logger


class AcceptContractCase(BaseRepresCase):
    """
    Принятие договора
    """

    def __init__(self, repres_repo: Type[RepresRepo]) -> None:
        self.repres_repo: RepresRepo = repres_repo()
        self.repres_update = user_changes_logger(
            self.repres_repo.update, self, content="Принятие договора представителя"
        )

    async def __call__(self, repres_id: int, payload: RequestAcceptContractModel) -> User:
        data: dict[str, Any] = payload.dict()
        filters: dict[str, Any] = dict(id=repres_id)
        repres: User = await self.repres_repo.retrieve(filters=filters)
        await self.repres_update(repres, data=data)
        return repres
