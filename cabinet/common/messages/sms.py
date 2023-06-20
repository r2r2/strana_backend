from asyncio import Future, Task, create_task, ensure_future
from typing import Any, Optional, Type
from tortoise import Tortoise
from copy import copy

from config import sms_center_config, tortoise_config

from .repos import LogSmsRepo
from ..requests import CommonRequest


class SmsService:
    """
    Sms service
    """

    def __init__(
        self,
        message: str,
        phone: str,
        tiny_url: bool = False,
        imgcode: Optional[str] = None,
        userip: Optional[str] = None,
        lk_type: Optional[str] = None,
        sms_event_slug: Optional[str] = None,
    ) -> None:
        self.phone: str = phone
        self.message: str = message
        self.tiny_url: bool = tiny_url
        self.imgcode: Optional[str] = imgcode
        self.userip: Optional[str] = userip

        self.url: str = sms_center_config["url"]
        self.login: str = sms_center_config["login"]
        self.password: str = sms_center_config["password"]
        self.lk_type: Optional[str] = lk_type
        self.sms_event_slug: Optional[str] = sms_event_slug
        self.log_sms_repo: LogSmsRepo = LogSmsRepo()
        self.orm_class: Type[Tortoise] = Tortoise
        self.orm_config: dict[str, Any] = copy(tortoise_config)
        if self.orm_config:
            self.orm_config.pop("generate_schemas", None)

    def as_task(self) -> Task:
        return create_task(self())

    def as_future(self) -> Future:
        return ensure_future(self())

    async def __call__(self) -> bool:

        log_sms = await self._loging_sms(is_sent=True)

        options: dict[str, Any] = dict(
            url=self.url,
            method="POST",
            query=dict(
                login=self.login,
                psw=self.password,
                phones=self.phone,
                mes=self.message,
                tinyurl=self.tiny_url,
                imgcode=self.imgcode,
                userapi=self.userip,
            ),
        )
        async with CommonRequest(**options) as response:
            response_ok: bool = response.ok

        if not response_ok:
            await self.log_sms_repo.update(model=log_sms, data=dict(is_sent=False))

        return response_ok

    async def _loging_sms(self, is_sent: bool):
        """
        Логируем отправленное смс сообщение в админке через селери таску.
        """
        data = dict(
            text=self.message,
            lk_type=self.lk_type,
            sms_event_slug=self.sms_event_slug,
            recipient_phone=self.phone,
            is_sent=is_sent,
        )
        return await self.log_sms_repo.create(data=data)
