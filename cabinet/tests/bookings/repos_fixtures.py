from datetime import datetime, timedelta

import pytest
from importlib import import_module

from pytz import UTC

from src.booking.repos import BookingRepo, Booking, BookingSourceRepo


@pytest.fixture(scope="function")
def booking_repo() -> BookingRepo:
    return getattr(import_module("src.booking.repos"), "BookingRepo")()


@pytest.fixture(scope="function")
async def booking(booking_repo, property) -> Booking:
    await property.fetch_related("building__booking_types")
    booking_type = await property.building.booking_types[0]
    data = {
        "booking_period": booking_type.period,
        "until": datetime.now(tz=UTC) + timedelta(days=booking_type.period),
        "expires": datetime.now(tz=UTC) + timedelta(minutes=30),
        "floor_id": property.floor_id,
        "project_id": property.project_id,
        "building_id": property.building_id,
        "property_id": property.id,
        "payment_amount": booking_type.price,
        "contract_accepted": True,
    }
    booking = await booking_repo.create(data)
    return booking


@pytest.fixture(scope="function")
def booking_source_repo() -> BookingSourceRepo:
    return getattr(import_module("src.booking.repos"), "BookingSourceRepo")()


@pytest.fixture(scope="function")
async def booking_source_amocrm(booking_source_repo,) -> Booking:
    data = {
        "name": "Импортирован из AMOCRM",
        "slug": "amocrm",
    }
    booking_source = await booking_source_repo.create(data)
    return booking_source
