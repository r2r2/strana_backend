from http import HTTPStatus
from typing import Any, Coroutine, Callable

from aiohttp import ClientSession, TCPConnector

from common.depreg.dto.depreg_response import DepregParticipantsDTO
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
        self._token: str = config["token"]

    async def get_participants(
        self,
        event_id: int,
        fields: str | None = None,
        page: int | None = None
    ) -> DepregParticipantsDTO:
        """
        Позволяет получить постраничный доступ к списку участников мероприятия.

        Parameters:
            filter[eventId]* (integer): ID события; required: true;
            fields (string): Список полей, разделённых запятыми, которые будут возвращены.;
            page (integer): Страница списка; minimum: 1

        Responses:
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
        }
        if fields:
            query_params["fields"] = fields
        if page:
            query_params["page"] = page

        request_data: dict[str, Any] = dict(
            url=self._base_url + "/participants",
            method="GET",
            query=query_params,
            session=self._session,
            headers=self._headers,
            auth_type=self._auth_type,
            token=self._token,
        )
        response: CommonResponse = await self._make_request(request_data)
        return DepregParticipantsDTO(**{"data": response.data})

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
