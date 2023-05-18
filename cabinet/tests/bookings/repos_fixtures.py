import pytest
from importlib import import_module

from src.booking.repos import BookingRepo


@pytest.fixture(scope="function")
def booking_repo() -> BookingRepo:
    return getattr(import_module("src.booking.repos"), "BookingRepo")()
