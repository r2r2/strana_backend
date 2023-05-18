from secrets import token_urlsafe
from typing import Type, Any, Callable

from .base_proceed_changes import BaseProceedPhoneChanges
from ..types import RepresSms
from ..repos import RepresRepo, User
from ..models import RequestInitializeChangePhone
from ..exceptions import RepresNotFoundError, RepresPhoneTakenError
from ...users.loggers.wrappers import user_changes_logger


class InitializeChangePhoneCase(BaseProceedPhoneChanges):
    """
    Обновление телефона агентом
    """

    def __init__(
        self,
        user_type: str,
        sms_class: Type[RepresSms],
        repres_repo: Type[RepresRepo],
        site_config: dict[str, Any],
        token_creator: Callable[[int], str],
    ) -> None:
        self.repres_repo: RepresRepo = repres_repo()
        self.repres_update = user_changes_logger(
            self.repres_repo.update, self, content="Обновление номера телефона представителя"
        )
        self.user_type: str = user_type
        self.sms_class: Type[RepresSms] = sms_class
        self.token_creator: Callable[[int], str] = token_creator
        self.site_host: str = site_config["site_host"]

    async def __call__(self, repres_id: int, payload: RequestInitializeChangePhone) -> User:
        phone = payload.phone
        filters: dict[str, Any] = dict(id=repres_id, is_deleted=False, type=self.user_type)
        repres: User = await self.repres_repo.retrieve(filters=filters)
        if not repres:
            raise RepresNotFoundError
        filters: dict[str, Any] = dict(phone=phone)
        user: User = await self.repres_repo.retrieve(filters=filters)
        if user and user.id != repres.id:
            raise RepresPhoneTakenError

        data = dict()
        data["change_phone"]: str = phone
        data["change_phone_token"]: str = token_urlsafe(32)
        phone_token: str = self.token_creator(repres.id)
        repres: User = await self.repres_update(repres, data=data)
        await self._send_sms(repres=repres, token=phone_token)
        return repres
