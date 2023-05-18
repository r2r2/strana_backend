from asyncio import Task
from secrets import token_urlsafe
from typing import Type, Callable, Union, Any

from ..entities import BaseRepresCase
from ..repos import RepresRepo, User
from ..types import RepresEmail


class ChangeEmailCase(BaseRepresCase):
    """
    Смена почты
    """

    template: str = "src/represes/templates/confirm_email.html"
    link: str = "https://{}/confirm/represes/confirm_email?q={}&p={}"

    fail_link: str = "https://{}/account/represes"
    success_link: str = "https://{}/account/represes"

    def __init__(
        self,
        user_type: str,
        repres_repo: Type[RepresRepo],
        site_config: dict[str, Any],
        email_class: Type[RepresEmail],
        token_creator: Callable[[int], str],
        token_decoder: Callable[[str], Union[int, None]],
    ) -> None:
        self.repres_repo: RepresRepo = repres_repo()

        self.email_class: Type[RepresEmail] = email_class
        self.token_creator: Callable[[int], str] = token_creator
        self.token_decoder: Callable[[str], Union[int, None]] = token_decoder

        self.user_type: str = user_type
        self.lk_site_host: str = site_config["lk_site_host"]
        self.broker_site_host: str = site_config["broker_site_host"]

    async def __call__(self, token: str, change_email_token: str) -> str:
        repres_id: Union[int, None] = self.token_decoder(token)
        filters: dict[str, Any] = dict(
            id=repres_id,
            is_active=True,
            is_approved=True,
            is_deleted=False,
            type=self.user_type,
            change_email_token=change_email_token,
        )
        repres: User = await self.repres_repo.retrieve(filters=filters)
        filters: dict[str, Any] = dict(email__iexact=repres.change_email)
        other_repres: User = await self.repres_repo.retrieve(filters=filters)
        link: str = self.fail_link.format(self.broker_site_host)
        if repres and not other_repres:
            data: dict[str, Any] = dict(
                is_active=False,
                change_email=None,
                change_email_token=None,
                email=repres.change_email,
                email_token=token_urlsafe(32),
            )
            token: str = self.token_creator(repres.id)
            await self.repres_repo.update(repres, data=data)
            await self._send_email(repres=repres, token=token)
            link: str = self.success_link.format(self.broker_site_host)
        return link

    async def _send_email(self, repres: User, token: str) -> Task:
        confirm_link: str = self.link.format(self.lk_site_host, token, repres.email_token)
        email_options: dict[str, Any] = dict(
            topic="Подтверждение почты",
            recipients=[repres.email],
            template=self.template,
            context=dict(confirm_link=confirm_link),
        )
        email_service: RepresEmail = self.email_class(**email_options)
        return email_service.as_task()
