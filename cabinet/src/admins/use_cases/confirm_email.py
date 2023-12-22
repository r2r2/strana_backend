from typing import Type, Callable, Union, Any

from ..repos import AdminRepo, User
from ..entities import BaseAdminCase
from src.users.loggers.wrappers import user_changes_logger
from common.schemas import UrlEncodeDTO
from common.utils import generate_notify_url


class ConfirmEmailCase(BaseAdminCase):
    """
    Подтверждение email
    """
    # а в чем разница? они одинаковые
    fail_link: str = "https://{}/account/admins/email-confirmed" 
    success_link: str = "https://{}/account/admins/email-confirmed"

    common_link_route_template: str = "/account/admins/email-confirmed"

    def __init__(
        self,
        user_type: str,
        admin_repo: Type[AdminRepo],
        site_config: dict[str, Any],
        token_decoder: Callable[[str], Union[int, None]],
    ) -> None:
        self.admin_repo: AdminRepo = admin_repo()
        self.admin_update = user_changes_logger(
            self.admin_repo.update, self, content="Подтверждение email админа"
        )

        self.user_type: str = user_type
        self.token_decoder: Callable[[str], Union[int, None]] = token_decoder

        self.site_host: str = site_config["broker_site_host"]

    async def __call__(self, token: str, email_token: str) -> str:
        admin_id: Union[int, None] = self.token_decoder(token)
        filters: dict[str, Any] = dict(
            id=admin_id, email_token=email_token, type=self.user_type, is_active=False
        )
        admin: User = await self.admin_repo.retrieve(filters=filters)

        common_data: dict[str, Any] = dict(
            host=self.site_host,
            route_template=self.common_link_route_template,
        )
        url_dto: UrlEncodeDTO = UrlEncodeDTO(**common_data)
        link: str = generate_notify_url(url_dto=url_dto)
        if admin:
            data: dict[str, Any] = dict(is_active=True, email_token=None)
            await self.admin_update(admin, data=data)
        return link
