from datetime import datetime, timedelta
from types import TracebackType
from typing import Any, Callable, Coroutine, Optional, Type, Union
from enum import Enum

import structlog
from aiohttp import ClientSession
from config import profitbase_config

from ..requests import CommonRequest, CommonResponse
from ..wrappers import mark_async
from .decorators import refresh_on_status


class ProfitbaseStatuses(str, Enum):
    AVAILABLE = "AVAILABLE"
    BOOKED = "BOOKED"


@mark_async
class ProfitBase:
    """
    Profitbase integration
    """

    status_success: str = "AVAILABLE"
    dealed_code: str = "property_already_in_deal"
    status_mapping: dict[str, str] = {
        "UNAVAILABLE": "SOLD",
        "AVAILABLE": "FREE",
        "BOOKED": "BOOKED",
        "EXECUTION": "SOLD",
        "SOLD": "SOLD",
    }

    _type: str = "api-app"
    _refresh_statuses: tuple[int] = (401, 403)
    _default_headers: dict[str, str] = {"Content-Type": "application/json"}
    _request_timeout: Optional[int] = 60

    logger = structlog.get_logger("profitbase")

    async def __ainit__(self) -> None:
        self.errors: bool = False
        self._session: ClientSession = ClientSession()
        self._request_class: Type[CommonRequest] = CommonRequest

        self._url: str = profitbase_config["url"]
        self._api_key: str = profitbase_config["api_key"]
        self._auth_url: str = profitbase_config["url"] + profitbase_config["auth_route"]

        self._access_token: str = None
        self._expire_time: datetime = None

        await self._refresh_auth()

    @property
    def _auth_query(self) -> dict[str, str]:
        """
        Query for auth-required endpoints
        """
        auth_query: dict[str, str] = dict(access_token=self._access_token)
        return auth_query

    async def _refresh_auth(self) -> None:
        """
        Refreshing authorization
        """
        payload: dict[str, Any] = dict(type=self._type, credentials=dict(pb_api_key=self._api_key))
        request_options: dict[str, Any] = self.__get_auth_options(payload=payload)
        refresh_auth: CommonRequest = self._request_class(**request_options)
        response: CommonResponse = await refresh_auth()
        self.logger.debug("Profitbase auth", response=response.data)
        if "access_token" in response.data:
            self._access_token: str = response.data["access_token"]
            self._expire_time: datetime = datetime.now() + timedelta(
                seconds=response.data["remaining_time"]
            )
        else:
            self.errors: bool = True

    async def __aenter__(self) -> "ProfitBase":
        """
        Nothing on entering context manager
        """
        return self

    async def book_property(self, property_id: int, deal_id: int) -> dict[str, Any]:
        """
        Booking property on profitbase
        """
        route: str = "/crm/addPropertyDeal"
        payload: dict[str, Any] = dict(propertyId=property_id, dealId=deal_id)
        response: CommonResponse = await self._request_post(route=route, payload=payload)
        print("Profitbase response status", response.status)
        print("Profitbase response errors", response.errors)
        data: dict[str, Any] = response.data
        return data

    async def change_property_status(self, property_id: int, status: ProfitbaseStatuses):
        """
        Chenge property status profitbase
        """
        route: str = f"/properties/{property_id}/status-change"
        payload: Union[dict[str, Any], str] = status
        response: CommonResponse = await self._request_post(route=route, payload=payload)
        data: dict[str, Any] = response.data
        return data

    async def deals_list(self, property_id: int):
        """
        Deals list of property
        """
        route: str = f"/get-property-deals?ids={property_id}"
        response: CommonResponse = await self._request_get(route=route)
        data: dict[str, Any] = response.data
        return data

    async def unbook_property(self, deal_id: int) -> dict[str, Any]:
        """
        Unbooking property on profitbase
        """
        route: str = "/crm/removePropertyDeal"
        payload: dict[str, Any] = dict(dealId=deal_id)
        response: CommonResponse = await self._request_post(route=route, payload=payload)
        data: dict[str, Any] = response.data
        print("Unbooking response", data)
        return data

    async def get_property(self, property_id: int, full: bool = False) -> Optional[dict[str, Any]]:
        """
        Получение данных о конкретной квартире
        """
        route: str = "/property"
        response: CommonResponse = await self._request_get(
            route=route, query=dict(id=property_id, full=full)
        )
        data: Union[list[Any], None] = response.data.get("data", None)
        if data is None or len(data) == 0:
            return None

        return data[0]

    async def get_property_history(self, property_id: int) -> list[Any]:
        """
        Getting property history from profitbase
        """
        route: str = f"/property/history/{property_id}"
        response: CommonResponse = await self._request_get(route=route)
        data: Union[list[Any], None] = response.data.get("response", None)
        return data

    @refresh_on_status
    async def _request_get(
        self, route: str, query: Optional[dict[str, Any]] = None
    ) -> CommonResponse:
        """
        Get request execution
        """
        if query is None:
            query = {}
        request_options: dict[str, Any] = self.__get_get_options(
            route=route, query={**query, **self._auth_query}
        )
        print("Request options:", request_options)
        request_get: Callable[..., Coroutine] = self._request_class(**request_options)
        response: CommonResponse = await request_get()
        return response

    @refresh_on_status
    async def _request_post(self, route: str, payload: Union[dict[str, Any], Any]) -> CommonResponse:
        """
        Post request execution
        """
        request_options: dict[str, Any] = self.__get_post_options(
            route=route, payload=payload, query=self._auth_query
        )
        request_post: Callable[..., Coroutine] = self._request_class(**request_options)
        response: CommonResponse = await request_post()
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
            timeout=self._request_timeout,
        )
        return options

    def __get_post_options(
        self, route: str, payload: Union[dict[str, Any], Any], query: dict[str, Any]
    ) -> dict[str, Any]:
        """
        Params for post request
        """
        options: dict[str, Any] = dict(
            method="POST",
            payload=payload,
            query=query,
            url=f"{self._url}{route}",
            session=self._session,
            headers=self._default_headers,
            timeout=self._request_timeout,
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
            headers=self._default_headers,
            timeout=self._request_timeout,
        )
        return options
