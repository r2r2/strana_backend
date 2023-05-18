from pytz import UTC
from asyncio import sleep, create_task
from datetime import datetime, timedelta
from typing import Type, Callable, Union, Any

from ..entities import BaseRepresCase
from ..repos import RepresRepo, User
from ..types import RepresSession
from ...users.loggers.wrappers import user_changes_logger


class ResetPasswordCase(BaseRepresCase):
    """
    Сброс пароля
    """

    fail_link: str = "https://{}/account/represes/set-password"
    success_link: str = "https://{}/account/represes/set-password"

    def __init__(
        self,
        user_type: str,
        session: RepresSession,
        site_config: dict[str, Any],
        auth_config: dict[str, Any],
        session_config: dict[str, Any],
        repres_repo: Type[RepresRepo],
        token_decoder: Callable[[str], Union[int, None]],
    ) -> None:
        self.repres_repo: RepresRepo = repres_repo()
        self.repres_update = user_changes_logger(
            self.repres_repo.update, self, content="Обновление данных представителя"
        )

        self.user_type: str = user_type
        self.session: RepresSession = session
        self.token_decoder: Callable[[str], Union[int, None]] = token_decoder

        self.site_host: str = site_config["broker_site_host"]
        self.password_time: int = auth_config["password_time"]
        self.password_reset_key: str = session_config["password_reset_key"]

    async def __call__(self, token: str, discard_token: str) -> str:
        repres_id: Union[int, None] = self.token_decoder(token)
        filters: dict[str, Any] = dict(
            id=repres_id,
            is_active=True,
            is_approved=True,
            type=self.user_type,
            discard_token=discard_token,
        )
        repres: User = await self.repres_repo.retrieve(filters=filters)
        link: str = self.fail_link.format(self.site_host)
        if repres:
            link: str = self.success_link.format(self.site_host)
            self.session[self.password_reset_key]: int = repres_id
            await self.session.insert()
            data: dict[str, Any] = dict(
                discard_token=None,
                reset_time=datetime.now(tz=UTC) + timedelta(minutes=self.password_time),
            )
            await self.repres_update(repres, data=data)
            create_task(self._remove_discard())
        return link

    async def _remove_discard(self) -> bool:
        await sleep(self.password_time * 60)
        discard_id: Union[int, None] = await self.session.get(self.password_reset_key)
        if discard_id is not None:
            await self.session.pop(self.password_reset_key)
        return True
