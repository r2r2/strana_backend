import base64
from typing import Any

import pytest
from mock import AsyncMock, MagicMock, patch

from common import (
    sberbank,
    utils,
)
from src.booking import repos as booking_repos
from src.booking import tasks, use_cases
from src.booking.constants import PaymentView, BookingStages, PaymentStatuses, BookingSubstages
from src.booking.exceptions import BookingOnlinePaymentError
from src.booking.models import RequestCheckParamsModel
from src.booking.repos import Booking
from src.properties.repos import Property
from src.task_management.factories import UpdateTaskInstanceStatusServiceFactory
from src.users.repos import User


pytestmark = pytest.mark.asyncio


class TestCheckParams:

    def setup(self):
        update_task_instance_status_service = UpdateTaskInstanceStatusServiceFactory.create()
        resources: dict[str, Any] = dict(
            sberbank_class=sberbank.Sberbank,
            global_id_decoder=utils.from_global_id,
            booking_repo=booking_repos.BookingRepo,
            acquiring_repo=booking_repos.AcquiringRepo,
            create_booking_log_task=tasks.create_booking_log_task,
            update_task_instance_status_service=update_task_instance_status_service,
        )
        check_params: use_cases.CheckParamsCaseV2 = use_cases.CheckParamsCaseV2(**resources)
        return check_params

    @patch("src.booking.repos.BookingRepo.retrieve", new_callable=AsyncMock)
    @pytest.mark.parametrize(
        "payment_success",
        [
            True, False
        ]
    )
    async def test__call__(
        self,
        booking_retrieve,
        payment_success: bool,
    ):
        check_params = self.setup()

        # Mocks #################################################
        property_: Property = Property()
        property_.global_id = "Rm9vYmFy"

        booking: Booking = Booking()
        booking.id = 1111
        booking.property = property_
        if payment_success:
            payment: dict = {
                'orderId': '050533b6-160b-747d-9721-99ff023d26c8',
                'formUrl': 'https://securecardpayment.ru/payment'
            }
            booking.payment_id = payment['orderId']
            booking.payment_url = payment['formUrl']
            booking.payment_status = PaymentStatuses.PENDING
        else:
            payment: dict = {}
            booking.params_checked = False
            booking.amocrm_stage = BookingStages.BOOKING
            booking.payment_status = PaymentStatuses.FAILED
            booking.amocrm_substage = BookingSubstages.BOOKING

        profitbase_id = base64.b64decode(booking.property.global_id).decode("utf-8").split(":")[-1]

        user: User = User()
        user.id = 2222

        booking_retrieve.return_value = booking

        payload = RequestCheckParamsModel(
            params_checked=True,
            payment_page_view=PaymentView.DESKTOP,
        )

        check_params._booking_update = AsyncMock(return_value=booking)

        check_params._online_payment = AsyncMock(return_value=payment)

        check_params._booking_success_logger = AsyncMock(return_value=booking)

        check_params._booking_fail_logger = AsyncMock(return_value=booking)

        check_params.booking_check_logger = AsyncMock(return_value=booking)

        check_params._update_task_status = AsyncMock()
        check_params._get_booking = AsyncMock(return_value=booking)
        check_params._check_booking = MagicMock()

        # Execution #############################################
        if payment_success:
            result = await check_params(
                user_id=user.id,
                booking_id=booking.id,
                payload=payload,
            )
        else:
            with pytest.raises(BookingOnlinePaymentError):
                result = await check_params(
                    user_id=user.id,
                    booking_id=booking.id,
                    payload=payload,
                )

        # Assertions ############################################
        filters: dict[str, Any] = dict(active=True, id=booking.id, user_id=user.id)
        booking_retrieve.assert_awaited_once_with(
            filters=filters, related_fields=["user", "project__city", "property", "building"]
        )

        check_params._check_booking.assert_called_once_with(
            booking=booking,
            profitbase_id=profitbase_id,
        )

        check_params._booking_update.assert_awaited_once()
        check_params._online_payment.assert_awaited_once_with(
            booking=booking,
        )

        if payment_success:
            data: dict[str, Any] = dict(
                payment_id=booking.payment_id, payment_url=booking.payment_url, payment_status=PaymentStatuses.PENDING
            )
            check_params._booking_success_logger.assert_awaited_once_with(
                booking=booking,
                data=data
            )
            check_params._booking_fail_logger.assert_not_awaited()
            check_params._update_task_status.assert_awaited_once_with(
                booking=booking,
            )
            check_params._get_booking.assert_awaited_once_with(
                booking=booking,
                user_id=user.id,
            )

            assert result == booking

        else:
            data: dict[str, Any] = dict(
                params_checked=False,
                amocrm_stage=BookingStages.BOOKING,
                payment_status=PaymentStatuses.FAILED,
                amocrm_substage=BookingSubstages.BOOKING,
            )
            check_params._booking_fail_logger.assert_awaited_once_with(
                booking=booking,
                data=data,
            )
            check_params._booking_success_logger.assert_not_awaited()
