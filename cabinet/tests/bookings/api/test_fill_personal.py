from typing import Any
from unittest.mock import MagicMock

import pytest
from mock import AsyncMock, patch

from common import (
    utils,
)
from src.booking import repos as booking_repos
from src.booking import use_cases
from src.booking.constants import (
    BookingCreatedSources,
    PaymentStatuses,
    BookingSubstages,
    BookingStages,
)
from src.booking.models import RequestFillPersonalModel
from src.booking.repos import BookingSource, Booking
from src.buildings import repos as buildings_repos
from src.users.repos import User


pytestmark = pytest.mark.asyncio


class TestFillPersonal:

    def setup(self):
        resources: dict[str, Any] = dict(
            global_id_decoder=utils.from_global_id,
            booking_repo=booking_repos.BookingRepo,
            building_booking_type_repo=buildings_repos.BuildingBookingTypeRepo,
        )
        fill_personal: use_cases.FillPersonalCaseV2 = use_cases.FillPersonalCaseV2(**resources)
        return fill_personal

    @patch("src.booking.repos.BookingRepo.retrieve", new_callable=AsyncMock)
    @pytest.mark.parametrize(
        "booking_source_slug",
        [
            BookingCreatedSources.AMOCRM,
            BookingCreatedSources.LK,
        ]
    )
    async def test__call__(
        self,
        booking_retrieve,
        booking_source_slug,
    ):
        fill_personal = self.setup()

        # Mocks #################################################
        booking_source: BookingSource = BookingSource()
        booking_source.id = 3333
        booking_source.slug = booking_source_slug

        if booking_source_slug == BookingCreatedSources.AMOCRM:
            booking: Booking = Booking()
            booking.id = 1111
            booking.booking_source = booking_source
        else:
            booking: Booking = Booking()
            booking.id = 1111
            booking.booking_source = booking_source
            booking.tags = ["Онлайн-бронирование"]
            booking.amocrm_stage = BookingStages.BOOKING
            booking.payment_status = PaymentStatuses.CREATED
            booking.amocrm_substage = BookingSubstages.BOOKING

        user: User = User()
        user.id = 2222

        booking_retrieve.return_value = booking

        fill_personal._check_booking_step = MagicMock()

        fill_personal._fill_personal = AsyncMock(return_value=booking)
        fill_personal._booking_update = AsyncMock(return_value=booking)

        payload = RequestFillPersonalModel(
            personal_filled=True,
            email_force=True,
        )

        personal_filled_data: dict[str, bool] = dict(
            personal_filled=payload.personal_filled,
            email_force=payload.email_force,
        )
        test_data: dict = dict(
            booking_id=booking.id,
            user_id=user.id,
            payload=payload,
        )
        # Execute ###############################################
        result = await fill_personal(**test_data)

        # Asserts ###############################################
        booking_retrieve.assert_awaited_once_with(
            filters=dict(id=booking.id, user_id=user.id, active=True),
            related_fields=[
                "user",
                "project__city",
                "property",
                "building",
                "booking_source",
            ],
        )

        fill_personal._fill_personal.assert_awaited_once_with(
            booking=booking,
            user_id=user.id,
            data=personal_filled_data,
        )

        if booking_source_slug != BookingCreatedSources.AMOCRM:
            data = dict(
                tags=booking.tags,
                amocrm_stage=BookingStages.BOOKING,
                payment_status=PaymentStatuses.CREATED,
                amocrm_substage=BookingSubstages.BOOKING,
            )
            fill_personal._booking_update.assert_awaited_once_with(
                booking=booking,
                data=data,
            )
            fill_personal._check_booking_step.assert_called_once_with(booking=booking)

        assert result == booking
