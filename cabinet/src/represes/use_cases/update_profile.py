import asyncio
from typing import Type

from common.amocrm import AmoCRM
from src.represes.entities import BaseRepresCase
from src.represes.models import UpdateProfileModel
from src.represes.repos import User
from src.represes.exceptions import RepresNotFoundError
from src.represes.repos import RepresRepo
from src.users.loggers.wrappers import user_changes_logger


class UpdateProfileCase(BaseRepresCase):
    """
    Изменение персональных данных агента
    """

    def __init__(
            self,
            repres_repo: Type[RepresRepo],
            user_type: str,
            amocrm_class: Type[AmoCRM]
    ) -> None:
        self.repres_repo: RepresRepo = repres_repo()
        self.repres_update = user_changes_logger(
            self.repres_repo.update, self, content="Изменение данных представителя"
        )
        self.user_type = user_type
        self.amocrm_class = amocrm_class

    async def __call__(self, repres_id: int, payload: UpdateProfileModel) -> User:
        filters = dict(id=repres_id, type=self.user_type)
        repres: User = await self.repres_repo.retrieve(filters=filters)
        if not repres:
            raise RepresNotFoundError
        data = payload.dict()
        await asyncio.gather(
            self.repres_update(repres, data),
            self._update_amo_info(repres, payload)
        )

        repres: User = await self.repres_repo.retrieve(filters=filters, related_fields=["agency"])

        return repres

    async def _update_amo_info(self, repres: User, payload: UpdateProfileModel) -> None:
        """Invoke amo API"""
        # In AMO we have only one field for full name,
        # there is no separate field for patronymic
        async with await self.amocrm_class() as amocrm:
            await amocrm.update_contact(
                user_id=repres.amocrm_id,
                user_name=self._get_fullname(repres, payload),
            )

    @staticmethod
    def _get_fullname(repres: User, payload: UpdateProfileModel) -> str:
        name = payload.name or repres.name or ""
        surname = payload.surname or repres.surname or ""
        patronymic = payload.patronymic or repres.patronymic or ""
        return f"{surname} {name} {patronymic}"
