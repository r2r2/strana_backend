from typing import Callable, Coroutine, Any

from aiohttp import ClientSession, TCPConnector

from common.requests import CommonRequest, CommonResponse
from config import mc_backend_config, maintenance_settings
from src.mortgage.models import SendAmoDataSchema


class CalculatorAPI:
    SPEC = "/v1/loan-offers/specs"
    BANNER = "/v1/banners"
    SEND_AMO_DATA = "/v1/tickets/cabinet/send_amo_data"

    def __init__(
        self,
        request_class: type[CommonRequest] | None = None,
        calculator_config: mc_backend_config = None,
    ):
        if not request_class:
            request_class = CommonRequest
        if not calculator_config:
            calculator_config = mc_backend_config

        self._request_class = request_class
        self._url: str = calculator_config["url"]

        self._session: ClientSession = self._get_session()

    def _get_session(self) -> ClientSession:
        if maintenance_settings.get("environment", "dev"):
            self._session: ClientSession = ClientSession(connector=TCPConnector(verify_ssl=False))
        else:
            self._session: ClientSession = ClientSession()

        return self._session

    async def __aenter__(self) -> "CalculatorAPI":
        """
        Nothing on entering context manager
        """
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        if not self._session.closed:
            await self._session.close()

    async def get_loan_offers_spec(self, city: str) -> CommonResponse:
        request_data = dict(
            url=self._url + self.SPEC,
            method="GET",
            query=dict(city=city),
            session=self._session,
        )

        request_get: Callable[..., Coroutine] = self._request_class(**request_data)
        return await request_get()

    async def get_mortgage_calc_data(self, city_slug: str) -> CommonResponse:
        request_data: dict[str, Any] = dict(
            url=self._url + self.BANNER,
            method="GET",
            query=dict(city=city_slug)
        )
        request_get: Callable[..., Coroutine] = self._request_class(**request_data)
        return await request_get()

    async def send_amo_data(self, payload: SendAmoDataSchema, headers: dict[str, str]) -> CommonResponse:
        request_data: dict[str, Any] = dict(
            url=self._url + self.SEND_AMO_DATA,
            method="POST",
            json=payload.dict(),
            headers=headers,
        )
        request_post: Callable[..., Coroutine] = self._request_class(**request_data)
        return await request_post()
