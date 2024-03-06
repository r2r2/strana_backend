from unittest.mock import patch

import pytest
from mock import AsyncMock

from src.booking import repos as booking_repos
from src.booking import use_cases
from src.booking.exceptions import BookingNotFoundError
from src.booking.repos import Booking
from src.task_management.constants import FastBookingSlug, OnlineBookingSlug
from src.users.repos import User


pytestmark = pytest.mark.asyncio


class TestAcceptBooking:

    def setup(self):
        resources: dict = dict(
            booking_repo=booking_repos.BookingRepo,
        )
        accept_booking: use_cases.AcceptBookingCase = use_cases.AcceptBookingCase(
            **resources
        )
        return accept_booking

    @patch("src.booking.repos.BookingRepo.update", new_callable=AsyncMock)
    @patch("src.booking.repos.BookingRepo.retrieve", new_callable=AsyncMock)
    @patch("src.booking.use_cases.accept_booking.get_booking_tasks")
    @pytest.mark.parametrize("booking_found", [True, False])
    async def test__call__(
        self,
        _get_booking_tasks: AsyncMock,
        retrieve_,
        update_,
        booking_found: bool,
    ):
        accept_booking = self.setup()

        # Mocks #################################################
        user: User = User()
        user.id = 1111

        booking: Booking = Booking()
        booking.id = 2222
        booking.user_id = user.id
        booking.contract_accepted = False
        booking.active = True

        updated_booking: Booking = Booking()
        updated_booking.id = 2222
        updated_booking.user_id = user.id
        updated_booking.contract_accepted = True
        updated_booking.active = True

        booking_tasks: list = []

        booking_with_tasks: Booking = Booking()
        booking_with_tasks.id = 2222
        booking_with_tasks.user_id = user.id
        booking_with_tasks.contract_accepted = True
        booking_with_tasks.active = True
        booking_with_tasks.tasks = booking_tasks

        if booking_found:
            retrieve_.return_value = booking
        else:
            retrieve_.return_value = None

        update_.return_value = updated_booking

        _get_booking_tasks.return_value = booking_tasks

        # Execute ##################################################
        if not booking_found:
            with pytest.raises(BookingNotFoundError):
                result = await accept_booking(user_id=user.id, booking_id=booking.id)
        else:
            result = await accept_booking(user_id=user.id, booking_id=booking.id)

        # Assert ###################################################
        booking_filters: dict = dict(id=booking.id, user_id=user.id, contract_accepted=False, active=True)
        retrieve_.assert_awaited_once_with(filters=booking_filters)

        if booking_found:
            update_.assert_awaited_once_with(model=booking, data=dict(contract_accepted=True))

            interested_task_chains: list[str] = [
                OnlineBookingSlug.ACCEPT_OFFER.value,
                FastBookingSlug.ACCEPT_OFFER.value,
            ]
            _get_booking_tasks.assert_awaited_once_with(
                booking_id=updated_booking.id,
                task_chain_slug=interested_task_chains,
            )

            assert result == booking_with_tasks
