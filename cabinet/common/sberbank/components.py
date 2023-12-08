from json import dumps
from typing import Any, Union

from common.sentry.utils import send_sentry_log


class SberbankPay:
    """
    Sberbank payment integration
    """

    async def _pay(self) -> Union[dict[str, Any], str]:
        if self._pay_data:
            pay_data: Union[list[Any], dict[str, Any], str] = self._pay_data
        else:
            request_options: dict[str, Any] = dict(
                url=self._pay_url,
                method="POST",
                headers=self._headers,
                query=self._form_pay_query(),
            )
            await send_sentry_log(
                tag="acquiring",
                message=f"SberbankPay request: {self._booking_order_id}",
                context={"request_options": request_options},
            )
            print("Request options: ", request_options)
            async with self._request_class(**request_options) as response:
                if not response.ok:
                    pay_data: dict[str, Any] = dict()
                    self._pay_data: dict[str, Any] = pay_data
                else:
                    pay_data: Union[list[Any], dict[str, Any], str] = response.data
                    self._pay_data: Union[list[Any], dict[str, Any], str] = pay_data

                await send_sentry_log(
                    tag="acquiring",
                    message=f"SberbankPay response: {self._booking_order_id}",
                    context={"response": response.data, "status": response.status},
                )
                print("Response data: ", response.data)
                print("Response status: ", response.status)
                print("Pay data: ", pay_data)
        print("Pay data: ", pay_data)
        return pay_data

    def _form_pay_query(self) -> dict[str, Any]:
        pay_query: dict[str, Any] = dict(
            userName=self._username,
            password=self._password,
            returnUrl=self._return_url,
            failUrl=self._fail_url,
            sessionTimeoutSecs=self._timeout,
            pageView=self._page_view,
            amount=self._booking_price,
            orderNumber=self._booking_order_number,
            orderBundle=self._form_pay_bundle(),
        )
        return pay_query

    def _form_pay_bundle(self) -> str:
        pay_bundle: dict[str, Any] = dict(
            customerDetails=dict(
                phone=self._user_phone, fullName=self._user_full_name
            ),
            cartItems=dict(
                items=[
                    dict(
                        name=self._property_name,
                        positionId=self._property_position_id,
                        quantity=dict(
                            value=self._property_quantity, measure=self._property_quantity_measure
                        ),
                        tax=dict(taxType=self._property_tax_type, taxSum=self._property_tax),
                        itemCurrency=self._booking_currency,
                        itemCode=self._property_id,
                        itemPrice=self._booking_price,
                        itemAmount=self._booking_price,
                        itemDetails=dict(
                            itemDetailsParams=[
                                dict(value=self._description, name=self._property_name)
                            ]
                        ),
                        itemAttributes=dict(
                            attributes=[
                                dict(name="paymentMethod", value=self._payment_method),
                                dict(name="paymentObject", value=self._payment_object),
                            ]
                        ),
                    )
                ]
            ),
        )
        return dumps(pay_bundle)


class SberbankStatus:
    """
    Sberbank status integration
    """

    async def _status(self) -> Union[list[Any], dict[str, Any], str]:
        if self._status_data:
            status_data: Union[list[Any], dict[str, Any], str] = self._status_data
        else:
            request_options: dict[str, Any] = dict(
                url=self._status_url,
                method="POST",
                headers=self._headers,
                query=self._form_status_query(),
            )
            await send_sentry_log(
                tag="acquiring",
                message=f"SberbankStatus request: {self._booking_order_id}",
                context={"request_options": request_options},
            )
            async with self._request_class(**request_options) as response:
                status_data: Union[list[Any], dict[str, Any], str] = response.data
                self._status_data: Union[list[Any], dict[str, Any], str] = status_data
                await send_sentry_log(
                    tag="acquiring",
                    message=f"SberbankStatus response: {self._booking_order_id}",
                    context={"response": response.data, "status": response.status},
                )
        return status_data

    def _form_status_query(self) -> dict[str, Any]:
        status_query: dict[str, Any] = dict(
            userName=self._username,
            password=self._password,
            orderId=self._booking_order_id,
            orderNumber=self._booking_order_number,
        )
        return status_query
