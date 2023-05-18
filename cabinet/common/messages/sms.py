from asyncio import Future, Task, create_task, ensure_future
from typing import Any, Optional

from config import sms_center_config

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
    ) -> None:
        self.phone: str = phone
        self.message: str = message
        self.tiny_url: bool = tiny_url
        self.imgcode: Optional[str] = imgcode
        self.userip: Optional[str] = userip

        self.url: str = sms_center_config["url"]
        self.login: str = sms_center_config["login"]
        self.password: str = sms_center_config["password"]

    def as_task(self) -> Task:
        return create_task(self())

    def as_future(self) -> Future:
        return ensure_future(self())

    async def __call__(self) -> bool:
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
        return response_ok
