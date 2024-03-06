from typing import Callable, Coroutine, Any

from aiohttp import ClientSession, TCPConnector

from common.requests import CommonRequest, CommonResponse
from config import mc_loyalty_config, maintenance_settings, EnvTypes
from src.booking.constants import CancelRewardComment


class LoyaltyAPI:
    CANCEL_REWARD_WEBHOOK = "/points/lk_webhook_cancel_reward_from_booking/{secret}"

    def __init__(
        self,
        request_class: type[CommonRequest] | None = None,
        loyalty_config: mc_loyalty_config = None,
    ):
        if not request_class:
            request_class = CommonRequest
        if not loyalty_config:
            loyalty_config = mc_loyalty_config

        self._request_class = request_class
        self._url: str = loyalty_config["url"]

        self._session: ClientSession = self._get_session()

    def _get_session(self) -> ClientSession:
        if maintenance_settings.get("environment") == EnvTypes.DEV:
            self._session: ClientSession = ClientSession(connector=TCPConnector(verify_ssl=False))
        else:
            self._session: ClientSession = ClientSession()

        return self._session

    async def __aenter__(self) -> "LoyaltyAPI":
        """
        Nothing on entering context manager
        """
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        if not self._session.closed:
            await self._session.close()

    async def cancel_booking_reward(
        self,
        booking_amocrm_id: int,
        comment: CancelRewardComment,
    ) -> CommonResponse:
        secret: str = mc_loyalty_config["loyalty_secret"]
        request_data: dict[str, Any] = dict(
            url=self._url + self.CANCEL_REWARD_WEBHOOK.format(secret=secret),
            method="POST",
            json=dict(booking_amocrm_id=booking_amocrm_id, comment=comment),
        )
        request_post: Callable[..., Coroutine] = self._request_class(**request_data)
        return await request_post()
