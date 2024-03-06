from types import TracebackType
from typing import Any, Callable, Coroutine, Type

import structlog
from aiohttp import ClientSession
from config import bitrix_config

from ..requests import CommonRequest, CommonResponse
from ..wrappers import mark_async


@mark_async
class Bitrix:
    """
    Bitrix integration
    """

    _type: str = "api-app"
    _refresh_statuses: tuple[int] = (401, 403)
    _default_headers: dict[str, str] = {"Content-Type": "application/json"}
    _request_timeout: int | None = 60

    logger = structlog.get_logger("bitrix")

    async def __ainit__(self) -> None:
        self.errors: bool = False
        self._session: ClientSession = ClientSession()
        self._request_class: Type[CommonRequest] = CommonRequest
        self._url: str = bitrix_config["bitrix_url"]
        self._user: str = bitrix_config["bitrix_user"]
        self._secret: str = bitrix_config["bitrix_secret"]
        self._chat: str = bitrix_config["bitrix_chat"]

    async def __aenter__(self) -> "Bitrix":
        """
        Nothing on entering context manager
        """
        return self

    async def send_message_in_chat(self, message: str) -> dict[str, Any]:
        """
        Send message to Bitrix
        """
        route: str = "/im.message.add.json"
        payload: dict[str, Any] = dict(DIALOG_ID=self._chat, MESSAGE=message)
        response: CommonResponse = await self._request_post(route=route, payload=payload)
        print("Bitrix response status", response.status)
        print("Bitrix response errors", response.errors)
        data: dict[str, Any] = response.data
        return data

    async def _request_post(self, route: str, payload: dict[str, Any] | Any) -> CommonResponse:
        """
        Post request execution
        """
        request_options: dict[str, Any] = self.__get_post_options(
            route=route, payload=payload
        )
        request_post: Callable[..., Coroutine] = self._request_class(**request_options)
        response: CommonResponse = await request_post()
        return response

    async def __aexit__(
        self,
        exc_type: Type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None:
        """
        Closing session on exiting context manager
        """
        if not self._session.closed:
            await self._session.close()

    def __get_post_options(
        self, route: str, payload: dict[str, Any] | Any) -> dict[str, Any]:
        """
        Params for post request
        """
        options: dict[str, Any] = dict(
            method="POST",
            payload=payload,
            url=f"{self._url}{self._user}/{self._secret}{route}",
            session=self._session,
            headers=self._default_headers,
            timeout=self._request_timeout,
        )

        return options
