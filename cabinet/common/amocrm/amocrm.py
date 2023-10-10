from copy import copy
from types import TracebackType
from typing import Any, Callable, Coroutine, Optional, Type, Union

import structlog
from aiohttp import ClientSession, TCPConnector
from asyncpg import Connection, Record, connect
from config import amocrm_config, maintenance_settings, amocrm_config_old
from config.feature_flags import FeatureFlags

from common.unleash.client import UnleashClient
from ..requests import CommonRequest, CommonResponse
from ..wrappers import mark_async
from .components import (AmoCRMCompanies, AmoCRMContacts, AmoCRMInterface,
                         AmoCRMLeads, AmoCRMNotes, AmoCRMTasks)
from .decorators import refresh_on_status
from .exceptions import AmocrmHookError


@mark_async
class AmoCRM(
    AmoCRMContacts, AmoCRMLeads, AmoCRMNotes, AmoCRMTasks, AmoCRMCompanies, AmoCRMInterface
):
    """
    AmoCRM integration
    """

    _refresh_auth_fail_message = "ПРОИЗОШЛА ОШИБКА ПРИ ОБНОВЛЕНИИ ТОКЕНА АВТОРИЗАЦИИ AmoCRM!"

    _refresh_statuses: tuple[int] = (401, 403)
    _default_headers: dict[str, str] = {"Content-Type": "application/json"}

    async def __ainit__(self) -> None:
        self.logger: Optional[Any] = structlog.getLogger(__name__)
        self._session: ClientSession = ClientSession(
            connector=TCPConnector(verify_ssl=False)
        ) if maintenance_settings.get("environment", "dev") else ClientSession()
        self._request_class: Type[CommonRequest] = CommonRequest

        unleash_client = UnleashClient()
        strana_lk_2218_enable = unleash_client.is_enabled(FeatureFlags.strana_lk_2218)

        amocrm_conf = amocrm_config_old
        if strana_lk_2218_enable:
            amocrm_conf = amocrm_config

        self._url: str = amocrm_conf["url"] + amocrm_conf["api_route"]
        self._url_v4: str = amocrm_conf["url"] + amocrm_conf["api_route_v4"]
        self._table: str = amocrm_conf["db_table"]
        self._auth_url: str = amocrm_conf["url"] + amocrm_conf["auth_route"]
        self._connection_options: dict[str, str] = dict(
            host=amocrm_conf["db_host"],
            port=amocrm_conf["db_port"],
            user=amocrm_conf["db_user"],
            password=amocrm_conf["db_password"],
            database=amocrm_conf["db_name"],
        )

        print("----AMOCRM SETTINGS----")
        print("url: ", self._url)
        print("_connection_options: ", self._connection_options)
        print("-"*20)

        self._settings: dict[str, Any] = await self._fetch_settings()

        self._access_token: str = self._settings["access_token"]
        self._refresh_token: str = self._settings["refresh_token"]

    @property
    def _auth_headers(self) -> dict[str, str]:
        """
        Headers for auth-required endpoints
        """
        auth_headers: dict[str, str] = copy(self._default_headers)
        auth_headers["Authorization"]: str = f"Bearer {self._access_token}"
        return auth_headers

    async def _fetch_settings(self) -> dict[str, Any]:
        """
        Getting amocrm settings from database
        """
        connection: Connection = await connect(**self._connection_options)
        query: str = self.__get_select_query()
        settings: Record = await connection.fetchrow(query=query)
        await connection.close()
        settings_dict = dict(settings)
        print(f"Данные для авторизации из БД: {settings_dict}")
        return settings_dict

    async def _refresh_auth(self) -> None:
        """
        Refreshing authorization
        """
        payload: dict[str, Any] = dict(
            grant_type="refresh_token",
            client_id=self._settings["client_id"],
            redirect_uri=self._settings["redirect_uri"],
            client_secret=self._settings["client_secret"],
            refresh_token=self._settings["refresh_token"],
        )

        request_options: dict[str, Any] = self.__get_auth_options(payload=payload)
        refresh_auth: Callable[..., Coroutine] = self._request_class(**request_options)

        print("Запрос на обновление токена авторизации...")
        print(f"Request Options: {request_options}")
        response: CommonResponse = await refresh_auth()

        print(f"Response Status: {response.status}")
        print(f"Response Data: {response.data}")
        if "access_token" not in response.data:
            print(self._refresh_auth_fail_message)
            self._settings = await self._fetch_settings()
            self._access_token: str = self._settings["access_token"]
            self._refresh_token: str = self._settings["refresh_token"]
            return

        self._access_token: str = response.data["access_token"]
        self._refresh_token: str = response.data["refresh_token"]

        print("Обновление данных для авторизации в AmoCRM в БД...")
        db_update_status = await self._update_settings()
        print(f"status: {db_update_status}")

    async def _update_settings(self) -> str:
        """
        Updating amocrm config on database
        """
        connection: Connection = await connect(**self._connection_options)
        query: str = self.__get_update_query()
        status: str = await connection.execute(query=query)
        await connection.close()
        return status

    async def __aenter__(self) -> "AmoCRM":
        """
        Nothing on entering context manager
        """
        return self

    @refresh_on_status
    async def _request_get(self, route: str, query: dict[str, Any]) -> CommonResponse:
        """
        Get request execution
        """
        request_options: dict[str, Any] = self.__get_get_options(route=route, query=query)
        request_get: Callable[..., Coroutine] = self._request_class(**request_options)
        response: CommonResponse = await request_get()
        return response

    @refresh_on_status
    async def _request_get_v4(self, route: str, query: dict[str, Any]) -> CommonResponse:
        """
        Get request execution
        """
        request_options: dict[str, Any] = self.__get_get_options_v4(route=route, query=query)
        request_get: Callable[..., Coroutine] = self._request_class(**request_options)
        response: CommonResponse = await request_get()
        return response

    @refresh_on_status
    async def _request_post(self, route: str, payload: Union[dict[str, Any], list[Any]]) -> CommonResponse:
        """
        Post request execution
        """
        request_options: dict[str, Any] = self.__get_post_options(route=route, payload=payload)
        request_post: Callable[..., Coroutine] = self._request_class(**request_options)
        response: CommonResponse = await request_post()
        return response

    @refresh_on_status
    async def _request_post_v4(
        self,
        route: str,
        payload: Union[dict[str, Any], list[dict[str, Any]]],
    ) -> CommonResponse:
        """
        Post request execution
        """
        request_options: dict[str, Any] = self.__get_post_options_v4(route=route, payload=payload)
        request_post: Callable[..., Coroutine] = self._request_class(**request_options)
        response: CommonResponse = await request_post()
        return response

    @refresh_on_status
    async def _request_patch(self, route: str, payload: dict[str, Any]) -> CommonResponse:
        """
        Post request execution
        """
        request_options: dict[str, Any] = self.__get_patch_options(route=route, payload=payload)
        request_patch: Callable[..., Coroutine] = self._request_class(**request_options)
        response: CommonResponse = await request_patch()
        return response

    @refresh_on_status
    async def _request_patch_v4(
            self, route: str, payload: Union[dict[str, Any], list[Any]]) -> CommonResponse:
        """
        Patch HTTP запрос, использующий AmoCRM API v4
        """
        request_options: dict[str, Any] = self.__get_patch_options_v4(route=route, payload=payload)
        request_patch: Callable[..., Coroutine] = self._request_class(**request_options)
        response: CommonResponse = await request_patch()
        return response

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
        if exc_val and exc_type:
            if hasattr(exc_val, "reason"):
                raise exc_val
            raise AmocrmHookError(reason=f'{exc_type.__name__}: {exc_val}') from exc_val

    def __get_select_query(self) -> str:
        """
        Select query for amocrm config
        """
        query: str = f"SELECT * from {self._table}"
        return query

    def __get_update_query(self) -> str:
        """
        Update query for amocrm config
        """
        query: str = (
            f"UPDATE {self._table} "
            f"SET (access_token, refresh_token) = ('{self._access_token}', '{self._refresh_token}') "
            f"WHERE id = {self._settings['id']}"
        )
        return query

    def __get_auth_options(self, payload: dict[str, Any]) -> dict[str, Any]:
        """
        Params for auth request
        """
        options: dict[str, Any] = dict(
            method="POST",
            payload=payload,
            url=self._auth_url,
            session=self._session,
            headers=self._default_headers,
        )
        return options

    def __get_post_options(self, route: str, payload: Union[dict[str, Any], list[Any]]) -> dict[str, Any]:
        """
        Params for post request
        """
        options: dict[str, Any] = dict(
            method="POST",
            payload=payload,
            url=f"{self._url}{route}",
            session=self._session,
            headers=self._auth_headers,
        )
        return options

    def __get_post_options_v4(
        self,
        route: str,
        payload: Union[dict[str, Any], list[dict[str, Any]]],
    ) -> dict[str, Any]:
        """
        Params for post request
        """
        options: dict[str, Any] = dict(
            method="POST",
            payload=payload,
            url=f"{self._url_v4}{route}",
            session=self._session,
            headers=self._auth_headers,
        )
        return options

    def __get_patch_options(self, route: str, payload: dict[str, Any]) -> dict[str, Any]:
        """
        Params for post request
        """
        options: dict[str, Any] = dict(
            method="PATCH",
            payload=payload,
            url=f"{self._url}{route}",
            session=self._session,
            headers=self._auth_headers,
        )
        return options

    def __get_patch_options_v4(self, route: str, payload: dict[str, Any]) -> dict[str, Any]:
        """
        Параметры PATCH запроса
        """
        options: dict[str, Any] = dict(
            method="PATCH",
            payload=payload,
            url=f"{self._url_v4}{route}",
            session=self._session,
            headers=self._auth_headers,
        )
        return options

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

    def __get_get_options_v4(self, route: str, query: dict[str, Any]) -> dict[str, Any]:
        """
        Params for get request
        """
        options: dict[str, Any] = dict(
            method="GET",
            query=query,
            url=f"{self._url_v4}{route}",
            session=self._session,
            headers=self._auth_headers,
        )
        return options
