from typing import Any

from config import lk_admin_config
from ..entities import BaseUserCase


class SuperuserUserFillDataCase(BaseUserCase):
    """
    Обновление данных пользователей в АмоСРМ после изменения в админке брокера.
    """

    def __init__(
        self,
        export_user_in_amo_task: Any,
    ) -> None:
        self.export_user_in_amo_task = export_user_in_amo_task

    def __call__(
        self,
        user_id: int,
        data: str,
    ) -> None:

        if data == lk_admin_config["admin_export_key"]:
            self.export_user_in_amo_task.delay(user_id=user_id)
