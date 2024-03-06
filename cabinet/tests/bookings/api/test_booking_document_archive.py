from datetime import datetime, timedelta, UTC
from decimal import Decimal

import pytest

from starlette import status

pytestmark = pytest.mark.asyncio


class TestBookingPropertySpecs:
    URL: str = "/booking/documents/archive"

    async def test_get_document_from_archive_unauthorized(
            self,
            async_client,
            booking,
            booking_event_history,
    ):
        """
        Неавторизованный юзер пытается получить оферту
        """
        fake_event_history = booking_event_history

        headers = {}
        response = await async_client.get(
            f"{self.URL}/{booking.id}?booking_event_history_id={fake_event_history.id}",
            headers=headers
        )
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    async def test_get_document_from_archive(
            self,
            booking,
            async_client,
            user,
            user_authorization,
            booking_repo,
            property,
            booking_event,
            document_archive,
            booking_event_history_repo,
    ):
        """
        Все данные корректны, возвращаем подписанную оферту
        """
        booking_type = await property.building.booking_types[0]
        test_booking = await booking_repo.create(
            {
                "user": user,
                "booking_period": booking_type.period,
                "until": datetime.now(tz=UTC) + timedelta(days=booking_type.period),
                "expires": datetime.now(tz=UTC) + timedelta(minutes=30),
                "floor_id": property.floor_id,
                "project_id": property.project_id,
                "building_id": property.building_id,
                "property_id": property.id,
                "payment_amount": Decimal("10000.25"),
                "contract_accepted": True,
            }
        )
        test_event_history = await booking_event_history_repo.create(
            {
                "booking": test_booking,
                "actor": "Test Actor",
                "event": booking_event,
                "signed_offer": document_archive,
                "event_slug": "test-event-slug",
                "event_description": "Тестовое описание события",
                "date_time": datetime.strptime("2020-01-15", "%Y-%m-%d"),
                "event_type_name": "Тестовый тип события",
                "event_name": "Тестовое событие",
            }
        )

        headers = {"Authorization": user_authorization}
        response = await async_client.get(
            f"{self.URL}/{test_booking.id}?booking_event_history_id={test_event_history.id}",
            headers=headers
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.json()["signedOffer"]

    async def test_get_document_from_archive_empty_signed_offer(
            self,
            booking,
            async_client,
            user,
            user_authorization,
            booking_repo,
            property,
            booking_event,
            booking_event_history_repo,
    ):
        """
        В истории сделки нет подписанной оферты
        """
        booking_type = await property.building.booking_types[0]
        test_booking = await booking_repo.create(
            {
                "user": user,
                "booking_period": booking_type.period,
                "until": datetime.now(tz=UTC) + timedelta(days=booking_type.period),
                "expires": datetime.now(tz=UTC) + timedelta(minutes=30),
                "floor_id": property.floor_id,
                "project_id": property.project_id,
                "building_id": property.building_id,
                "property_id": property.id,
                "payment_amount": Decimal("2131231.25"),
                "contract_accepted": True,
            }
        )
        test_event_history = await booking_event_history_repo.create(
            {
                "booking": test_booking,
                "actor": "Test Actor",
                "event": booking_event,
                # "signed_offer": document_archive, История сделки без подписанного договора оферты
                "event_slug": "test-event-slug",
                "event_description": "Тестовое описание события",
                "date_time": datetime.strptime("2020-01-15", "%Y-%m-%d"),
                "event_type_name": "Тестовый тип события",
                "event_name": "Тестовое событие",
            }
        )

        headers = {"Authorization": user_authorization}
        response = await async_client.get(
            f"{self.URL}/{test_booking.id}?booking_event_history_id={test_event_history.id}",
            headers=headers
        )
        assert response.status_code == status.HTTP_404_NOT_FOUND
