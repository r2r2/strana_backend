from typing import Type, Any, Callable, Union

from ..entities import BaseUserCase
from ..repos import UserRepo, User
from ..loggers.wrappers import user_changes_logger


class ConfirmEmailCase(BaseUserCase):
    """
    Подтверждение email
    """
    fail_link: str = "https://{}"
    success_link: str = "https://{}"

    def __init__(
            self,
            user_type: str,
            user_repo: Type[UserRepo],
            site_config: dict[str, Any],
            token_decoder: Callable[[str], Union[int, None]]
    ) -> None:
        self.user_repo: UserRepo = user_repo()
        self.user_update = user_changes_logger(self.user_repo.update, self, content="Сброс почтового токена")

        self.user_type: str = user_type
        self.token_decoder: Callable[[str], Union[int, None]] = token_decoder

        self.site_host: str = site_config["site_host"]

    async def __call__(self, token: str, email_token: str) -> str:
        user_id: Union[int, None] = self.token_decoder(token)
        filters: dict[str, Any] = dict(id=user_id, email_token=email_token, type=self.user_type, is_active=False)
        user: User = await self.user_repo.retrieve(filters=filters)
        link: str = self.fail_link.format(self.site_host)
        if user:
            link: str = self.success_link.format(self.site_host)
            data: dict[str, Any] = dict(is_active=True, email_token=None)
            await self.user_update(user=user, data=data)
        return link
