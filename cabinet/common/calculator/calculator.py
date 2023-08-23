from typing import Type, Callable, Coroutine, Any

from aiohttp import ClientSession, TCPConnector

from common.requests import CommonRequest, CommonResponse
from config import mc_backend_config, maintenance_settings


class CalculatorAPI:
    SPEC = "/v1/loan-offers/specs"
    BANNER = "/v1/banners"

    def __init__(
            self,
            request_class: Type[CommonRequest],
            calculator_config: mc_backend_config
    ):
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
