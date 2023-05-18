from typing import Type, Callable, Union, Any

from ..repos import RepresRepo, User
from ..entities import BaseRepresCase


class ConfirmPhoneCase(BaseRepresCase):
    """
    Подтверждение телефона
    """

    fail_link: str = "https://{}/account/represes/phone-confirmed"
    success_link: str = "https://{}/account/represes/phone-confirmed"

    def __init__(
        self,
        user_type: str,
        repres_repo: Type[RepresRepo],
        site_config: dict[str, Any],
        token_decoder: Callable[[str], Union[int, None]],
    ) -> None:
        self.repres_repo: RepresRepo = repres_repo()

        self.user_type: str = user_type
        self.token_decoder: Callable[[str], Union[int, None]] = token_decoder

        self.site_host: str = site_config["broker_site_host"]

    async def __call__(self, token: str, phone_token: str) -> str:
        repres_id: Union[int, None] = self.token_decoder(token)
        filters: dict[str, Any] = dict(
            id=repres_id, phone_token=phone_token, type=self.user_type, is_active=False
        )
        repres: User = await self.repres_repo.retrieve(filters=filters)
        link: str = self.fail_link.format(self.site_host)
        if repres:
            link: str = self.success_link.format(self.site_host)
            data: dict[str, Any] = dict(phone_token=None)
            if not repres.email_token:
                data["is_active"]: bool = True
            await self.repres_repo.update(repres, data=data)
        return link
