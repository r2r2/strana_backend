from copy import copy
from types import TracebackType
from typing import Any, Optional, Type, Callable, Coroutine
import structlog
from fastapi.encoders import jsonable_encoder
from aiohttp import ClientSession, TCPConnector

from config import maintenance_settings, tilda_config
from common.tilda.interface import TildaInterface
from ..wrappers import mark_async
from ..requests import CommonRequest, CommonResponse
from .models.entities import TildaPostPayloadModel
from .exceptions import TildaIntegrationError


@mark_async
class Tilda(TildaInterface):
    """
    Tilda integration
    """

    _default_headers: dict[str, str] = {"Content-Type": "application/json"}

    async def __ainit__(self) -> None:
        self.logger: Optional[Any] = structlog.getLogger(__name__)
        self._session: ClientSession = ClientSession(
            connector=TCPConnector(verify_ssl=False)
        ) if maintenance_settings.get("environment", "dev") else ClientSession()
        self._request_class: Type[CommonRequest] = CommonRequest

        self._url: str = tilda_config["base_url"]
        self._client_id: str = tilda_config["client_id"]
        self._auth_token: str = tilda_config["auth_token"]

        print("----TILDA SETTINGS----")
        print(f"url: {self._url} _client_id= {self._client_id} _auth_token = {self._auth_token}")

    @property
    def _auth_headers(self) -> dict[str, str]:
        """
        Headers for auth-required endpoints
        """
        auth_headers: dict[str, str] = copy(self._default_headers)
        auth_headers["X-Client-Id"]: str = self._client_id
        auth_headers["X-Auth-Token"]: str = self._auth_token
        return auth_headers

    async def _request_get(self, route: str, query: dict[str, Any] = None) -> CommonResponse:
        """
        Get request execution
        """
        request_options: dict[str, Any] = self.__get_get_options(route=route, query=query)
        request_get: Callable[..., Coroutine] = self._request_class(**request_options)
        response: CommonResponse = await request_get()
        return response

    async def _request_post(self, route: str,
                            payload: TildaPostPayloadModel) -> CommonResponse:
        """
        Post request execution
        """
        request_options: dict[str, Any] = self.__get_post_options(route=route, payload=payload)
        request_post: Callable[..., Coroutine] = self._request_class(**request_options)
        response: CommonResponse = await request_post()
        return response

    def __get_get_options(self, route: str, query: dict[str, Any]) -> dict[str, Any]:
        """
        Params for get request
        """
        options: dict[str, Any] = dict(
            method="GET",
            query=query,
            url=f"{self._url}{route}",
            session=self._session,
            headers=self._auth_headers,
        )
        return options

    def __get_post_options(self, route: str, payload: TildaPostPayloadModel) -> dict[str, Any]:
        """
        Params for post request
        """

        payload = jsonable_encoder(payload)
        print(f'payload = {payload} type = {type(payload)}')
        options: dict[str, Any] = dict(
            method="POST",
            payload=payload,
            url=f"{self._url}{route}",
            session=self._session,
            headers=self._auth_headers,
        )
        print(f'options = {options} options = {type(options)}')
        return options

    async def save_kp(self, payload: TildaPostPayloadModel) -> CommonResponse:
        route = "save/"
        return await self._request_post(route, payload)

    async def get_kp(self):
        pass

    async def __aenter__(self) -> "Tilda":
        """
        Nothing on entering context manager
        """
        return self

    async def __aexit__(
        self,
        exc_type: Optional[Type[BaseException]],
        exc_val: Optional[BaseException],
        exc_tb: Optional[TracebackType],
    ) -> None:
        """
        Closing session on exiting context manager
        """
        if not self._session.closed:
            await self._session.close()
        print(f'exc_val = {exc_val} exc_type = {exc_type}')
        if exc_val and exc_type:
            if hasattr(exc_val, "reason"):
                raise exc_val
            raise TildaIntegrationError(reason=f'{exc_type.__name__}: {exc_val}') from exc_val
