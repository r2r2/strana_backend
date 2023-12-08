from asyncio import sleep

from config import lk_admin_config
from src.users.services import UpdateContactService
from ..entities import BaseUserCase


class SuperuserUserFillDataCase(BaseUserCase):
    """
    Обновление данных пользователей в АмоСРМ после изменения в админке брокера.
    """

    def __init__(
        self,
        export_user_in_amo_service: UpdateContactService,
    ) -> None:
        self.export_user_in_amo_service: UpdateContactService = export_user_in_amo_service

    async def __call__(
        self,
        user_id: int,
        data: str,
    ) -> None:

        if data == lk_admin_config["admin_export_key"]:
            await sleep(3)
            await self.export_user_in_amo_service(user_id=user_id)
