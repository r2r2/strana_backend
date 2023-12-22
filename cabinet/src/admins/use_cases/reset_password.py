from asyncio import sleep, create_task
from datetime import datetime, timedelta
from typing import Type, Callable, Union, Any
from pytz import UTC

from ..entities import BaseAdminCase
from ..repos import AdminRepo, User
from ..types import AdminSession
from src.users.loggers.wrappers import user_changes_logger
from common.schemas import UrlEncodeDTO
from common.utils import generate_notify_url

class ResetPasswordCase(BaseAdminCase):
    """
    Сброс пароля
    """

    fail_link: str = "https://{}/account/admins/set-password"
    success_link: str = "https://{}/account/admins/set-password"

    common_link_route_template: str = "/account/admins/set-password"

    def __init__(
        self,
        user_type: str,
        session: AdminSession,
        auth_config: dict[str, Any],
        site_config: dict[str, Any],
        session_config: dict[str, Any],
        admin_repo: Type[AdminRepo],
        token_decoder: Callable[[str], Union[int, None]],
    ) -> None:
        self.admin_repo: AdminRepo = admin_repo()
        self.admin_update = user_changes_logger(
            self.admin_repo.update, self, content="Смена пароля"
        )

        self.user_type: str = user_type
        self.session: AdminSession = session
        self.token_decoder: Callable[[str], Union[int, None]] = token_decoder

        self.site_host: str = site_config["broker_site_host"]
        self.password_time: int = auth_config["password_time"]
        self.password_reset_key: str = session_config["password_reset_key"]

    async def __call__(self, token: str, discard_token: str) -> str:
        admin_id: Union[int, None] = self.token_decoder(token)
        filters: dict[str, Any] = dict(
            id=admin_id,
            type=self.user_type,
            discard_token=discard_token,
        )
        admin: User = await self.admin_repo.retrieve(filters=filters)

        common_data: dict[str, Any] = dict(
            host=self.site_host,
            route_template=self.common_link_route_template,
        )
        url_dto: UrlEncodeDTO = UrlEncodeDTO(**common_data)
        link: str = generate_notify_url(url_dto=url_dto)
        if admin:
            self.session[self.password_reset_key]: int = admin_id
            await self.session.insert()
            data: dict[str, Any] = dict(
                discard_token=None,
                reset_time=datetime.now(tz=UTC) + timedelta(minutes=self.password_time),
            )
            await self.admin_update(admin, data=data)
            create_task(self._remove_discard())
        return link

    async def _remove_discard(self) -> bool:
        await sleep(self.password_time * 60)
        discard_id: Union[int, None] = await self.session.get(self.password_reset_key)
        if discard_id is not None:
            await self.session.pop(self.password_reset_key)
        return True
