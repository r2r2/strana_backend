from decimal import Decimal
from typing import Any, Callable, Coroutine, Literal, Type
from uuid import uuid4

from config import sberbank_config, site_config

from ..requests import CommonRequest
from .components import SberbankPay, SberbankStatus
from ..unleash.client import UnleashClient


class Sberbank(SberbankPay, SberbankStatus):
    """
    Sberbank integration
    https://securepayments.sberbank.ru/wiki/doku.php/integration:api:start#интерфейс_rest
    """

    def __init__(
        self,
        user_email: str,
        user_phone: str,
        user_full_name: str,
        property_id: int,
        property_name: str,
        booking_currency: int,
        booking_price: Decimal,
        booking_order_id: uuid4,
        booking_order_number: str,
        username: str,
        password: str,
        *,
        amocrm_id: int | None = None,
        timeout: int | None = None,
        page_view: str | None = None,
        description: str | None = None,
    ) -> None:
        self._request_class: Type[CommonRequest] = CommonRequest
        self._pay_data: list[Any] | dict[str, Any] | str | None = None
        self._status_data: list[Any] | dict[str, Any] | str | None = None
        self._headers: dict[str, str] = dict(Accept="application/json")
        self._username = username
        self._password = password

        self._booking_currency: int = booking_currency
        self._booking_order_id: str = str(booking_order_id)
        self._booking_order_number: str = booking_order_number
        self._booking_price: int = int(booking_price) * 100

        self._user_email: str = user_email
        self._user_phone: str = user_phone
        self._user_full_name: str = user_full_name

        self._property_quantity: int = 1
        self._property_tax_type: int = 0
        self._property_position_id: int = 1
        self._property_id: str = str(property_id)
        self._property_quantity_measure: str = "шт"
        self._property_name: str = str(property_name)
        self._property_tax: int = 0

        self._payment_method: int = 4
        self._payment_object: int = 4

        self._pay_url: str = sberbank_config["url"] + "register.do"
        self._status_url: str = sberbank_config["url"] + "getOrderStatusExtended.do"
        self._fail_url: str = (
            f"https://{site_config['site_host']}"
            f"{sberbank_config['return_url'].format(sberbank_config['secret'], 'fail')}"
        )
        self._return_url: str = (
            f"https://{site_config['site_host']}"
            f"{sberbank_config['return_url'].format(sberbank_config['secret'], 'success')}"
        )
        self._timeout: int = timeout if timeout else 1200
        self._page_view: str = page_view if page_view else "DESKTOP"
        self._description: str = description if description else str()
        self._amocrm_id: int | None = amocrm_id

    async def __call__(self, action: Literal["status", "pay"]) -> dict[str, Any] | str | list[Any] | None:
        method: Callable[..., Coroutine] | None = getattr(self, f"_{action}", None)
        if not method:
            raise AttributeError(f"{self.__class__.__name__} has no attribute {action}.")
        result: Any = await method()
        return result
