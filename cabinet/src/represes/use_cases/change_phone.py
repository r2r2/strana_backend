from asyncio import Task
from secrets import token_urlsafe
from typing import Type, Callable, Union, Any

from ..entities import BaseRepresCase
from ..repos import RepresRepo, User
from ..types import RepresSms


class ChangePhoneCase(BaseRepresCase):
    """
    Смена телефона
    """

    template: str = "Для подтверждения номера телефона перейдите по ссылке {confirm_link} . "
    link: str = "https://{}/confirm/represes/confirm_phone?q={}&p={}"

    fail_link: str = "https://{}/account/represes"
    success_link: str = "https://{}/account/represes"

    def __init__(
        self,
        user_type: str,
        repres_repo: Type[RepresRepo],
        site_config: dict[str, Any],
        sms_class: Type[RepresRepo],
        token_creator: Callable[[int], str],
        token_decoder: Callable[[str], Union[int, None]],
    ) -> None:
        self.repres_repo: RepresRepo = repres_repo()

        self.sms_class: Type[RepresRepo] = sms_class
        self.token_creator: Callable[[int], str] = token_creator
        self.token_decoder: Callable[[str], Union[int, None]] = token_decoder

        self.user_type: str = user_type
        self.lk_site_host: str = site_config["lk_site_host"]
        self.broker_site_host: str = site_config["broker_site_host"]

    async def __call__(self, token: str, change_phone_token: str) -> str:
        repres_id: Union[int, None] = self.token_decoder(token)
        filters: dict[str, Any] = dict(
            id=repres_id,
            is_active=True,
            is_approved=True,
            is_deleted=False,
            type=self.user_type,
            change_phone_token=change_phone_token,
        )
        repres: User = await self.repres_repo.retrieve(filters=filters)
        filters: dict[str, Any] = dict(phone=repres.change_phone)
        other_repres: User = await self.repres_repo.retrieve(filters=filters)
        link: str = self.fail_link.format(self.broker_site_host)
        if repres and not other_repres:
            data: dict[str, Any] = dict(
                is_active=False,
                change_phone=None,
                change_phone_token=None,
                phone=repres.change_phone,
                phone_token=token_urlsafe(32),
            )
            token: str = self.token_creator(repres.id)
            await self.repres_repo.update(repres, data=data)
            await self._send_sms(repres=repres, token=token)
            link: str = self.success_link.format(self.broker_site_host)
        return link

    async def _send_sms(self, repres: User, token: str) -> Task:
        confirm_link: str = self.link.format(self.lk_site_host, token, repres.change_phone_token)
        message: str = self.template.format(confirm_link=confirm_link)
        sms_options: dict[str, Any] = dict(phone=repres.phone, message=message)
        sms_service: RepresSms = self.sms_class(**sms_options)
        return sms_service.as_task()