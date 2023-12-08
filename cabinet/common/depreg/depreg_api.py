import asyncio
from http import HTTPStatus
from typing import Any, Coroutine, Callable

from aiohttp import ClientSession, TCPConnector

from common.depreg.dto import DepregParticipantsDTO, DepregGroupDTO
from common.depreg.exceptions import DepregAPIError
from common.requests import CommonRequest, CommonResponse
from config import maintenance_settings, depreg_config


class DepregAPI:
    """
    Интеграция с API Департамента Регистрации Мероприятий
    docs: https://app.swaggerhub.com/apis/cimmwolf/et.depreg.ru/2.1.0#/
    """
    _headers: dict[str, str] = {'accept': 'application/json'}

    def __init__(self, config: dict[str, Any] = None):
        self._request_class: type[CommonRequest] = CommonRequest
        self._session: ClientSession = self._get_session()

        if not config:
            config = depreg_config
        self._base_url: str = config["base_url"]
        self._auth_type: str = config["auth_type"]

    async def get_participants(
        self,
        event_id: int,
        token: str,
        fields: str | None = None,
        page: int = 1,
    ) -> DepregParticipantsDTO:
        """
        Позволяет получить постраничный доступ к списку участников мероприятия.

        Parameters API:
            filter[eventId]* (integer): ID события; required: true;
            fields (string): Список полей, разделённых запятыми, которые будут возвращены.;
            page (integer): Страница списка; minimum: 1

        Response example:
            [
              {
                "id": 0,
                "eventId": 0,
                "groupId": 0,
                "code": "string",
                "name": "Пантелеймон",
                "surname": "string",
                "patronymic": "string",
                "email": "user@example.com",
                "phone": "string",
                "company": "string",
                "info": {},
                "marked": true
              }
            ]
        """
        query_params: dict[str, Any] = {
            "filter[eventId]": event_id,
            "page": page,
        }
        if fields:
            query_params["fields"] = fields

        request_data: dict[str, Any] = dict(
            url=self._base_url + "/participants",
            method="GET",
            query=query_params,
            session=self._session,
            headers=self._headers,
            auth_type=self._auth_type,
            token=token,
        )
        response: CommonResponse = await self._make_request(request_data)
        response_data: list[dict[str, Any]] = []
        response_data.extend(response.data)

        page_count: int = int(response.raw.headers['X-Pagination-Page-Count'])
        current_page: int = int(response.raw.headers['X-Pagination-Current-Page'])

        await self._process_pagination(
            page_count=page_count,
            current_page=current_page,
            response_data=response_data,
            event_id=event_id,
            token=token,
        )

        return DepregParticipantsDTO(**{"data": response_data})

    async def _process_pagination(
        self,
        page_count: int,
        current_page: int,
        response_data: list[dict[str, Any]],
        event_id: int,
        token: str,
    ) -> None:
        async_tasks: list[Coroutine | None] = []
        for page in range(current_page + 1, page_count + 1):
            query_params: dict[str, Any] = {
                "filter[eventId]": event_id,
                "page": page,
            }
            request_data: dict[str, Any] = dict(
                url=self._base_url + "/participants",
                method="GET",
                query=query_params,
                session=self._session,
                headers=self._headers,
                auth_type=self._auth_type,
                token=token,
            )
            async_tasks.append(self._make_request(request_data))

        [response_data.extend(result.data) for result in await asyncio.gather(*async_tasks)]

    async def get_group_by_id(self, group_id: int, token: str) -> DepregGroupDTO:
        """
        Возвращает информацию о конкретной группе, чей ID указан в URL

        Parameters API:
            group_id* (integer): ID группы; required: true;

        Response example:
            {
              "id": 4584,
              "eventId": 1471,
              "templateId": null,
              "createdAt": "2023-10-10 13:45:24",
              "name": "14:00-15:00"
            }
        """
        request_data: dict[str, Any] = dict(
            url=self._base_url + f"/groups/{group_id}",
            method="GET",
            session=self._session,
            headers=self._headers,
            auth_type=self._auth_type,
            token=token,
        )
        response: CommonResponse = await self._make_request(request_data)
        return DepregGroupDTO(**response.data)

    async def _make_request(self, request_data: dict[str, Any]) -> CommonResponse:
        request_get: Callable[..., Coroutine] = self._request_class(**request_data)
        response = await request_get()
        if response.status == HTTPStatus.OK:
            return response
        raise DepregAPIError

    def _get_session(self) -> ClientSession:
        if maintenance_settings.get("environment", "dev"):
            return ClientSession(connector=TCPConnector(verify_ssl=False))
        return ClientSession()

    async def __aenter__(self) -> "DepregAPI":
        """
        Nothing on entering context manager
        """
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        if not self._session.closed:
            await self._session.close()
