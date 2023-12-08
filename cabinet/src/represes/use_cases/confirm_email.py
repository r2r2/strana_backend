from typing import Type, Callable, Union, Any

from ..repos import RepresRepo, User
from ..entities import BaseRepresCase
from common.schemas import UrlEncodeDTO
from common.utils import generate_notify_url
from src.users.loggers.wrappers import user_changes_logger


class ConfirmEmailCase(BaseRepresCase):
    """
    Подтверждение email
    """

    fail_link: str = "https://{}/account/represes/email-confirmed"
    success_link: str = "https://{}/account/represes/email-confirmed"

    common_link_route_template: str = "/account/represes/email-confirmed"

    def __init__(
        self,
        user_type: str,
        repres_repo: Type[RepresRepo],
        site_config: dict[str, Any],
        token_decoder: Callable[[str], Union[int, None]],
    ) -> None:
        self.repres_repo: RepresRepo = repres_repo()
        self.repres_update = user_changes_logger(
            self.repres_repo.update, self, content="Обновление данных представителя"
        )

        self.user_type: str = user_type
        self.token_decoder: Callable[[str], Union[int, None]] = token_decoder

        self.site_host: str = site_config["broker_site_host"]

    async def __call__(self, token: str, email_token: str) -> str:
        repres_id: Union[int, None] = self.token_decoder(token)
        filters: dict[str, Any] = dict(
            id=repres_id, email_token=email_token, type=self.user_type, is_active=False
        )
        repres: User = await self.repres_repo.retrieve(filters=filters)
        common_data: dict[str, Any] = dict(
            host=self.site_host,
            route_template = self.common_link_route_template,
        )
        url_dto: UrlEncodeDTO = UrlEncodeDTO(**common_data)
        link: str = generate_notify_url(url_dto=url_dto)
        if repres:
            data: dict[str, Any] = dict(email_token=None)
            if not repres.phone_token:
                data["is_active"]: bool = True
            await self.repres_update(repres, data=data)
        return link
