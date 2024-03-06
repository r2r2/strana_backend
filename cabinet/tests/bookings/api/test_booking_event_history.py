from datetime import datetime, UTC, timedelta

import pytest

from starlette import status

pytestmark = pytest.mark.asyncio


class TestBookingEventHistory:
    URL: str = "/booking/booking_event_history/"

    async def test_booking_event_histories_booking_not_exist(self, async_client, user_authorization):
        """
        Пытаемся получить историю несуществующей сделки
        """

        headers = {"Authorization": user_authorization}
        fake_booking_id = 2121212121212121212121

        response = await async_client.get(self.URL + str(fake_booking_id), headers=headers)
        assert response.status_code == status.HTTP_404_NOT_FOUND

    async def test_booking_event_histories(
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
        Корректный сценарий получения истории по существующей сделке
        """

        headers = {"Authorization": user_authorization}
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
                "payment_amount": booking_type.price,
                "contract_accepted": True,
            }
        )
        test_event_history = await booking_event_history_repo.create(
            {
                "booking": test_booking,
                "actor": "Test Actor",
                "event": booking_event,
                "event_slug": "test-event-slug",
                "event_description": "Тестовое описание события",
                "date_time": datetime.strptime("2020-01-15", "%Y-%m-%d"),
                "event_type_name": "Тестовый тип события",
                "event_name": "Тестовое событие",
                "group_status_until": "group_status_until",
                "group_status_after": "group_status_after",
                "task_name_until": "task_name_until",
                "task_name_after": "task_name_after",
                "event_status_until": "event_status_until",
                "event_status_after": "event_status_after",
            }
        )

        response = await async_client.get(self.URL + str(test_booking.id), headers=headers)

        assert response.status_code == status.HTTP_200_OK
        res_json = response.json()
        assert res_json["count"] == 1
        res_json_result = res_json["result"][0]
        assert res_json_result["id"]
        assert res_json_result["eventName"] == "Тестовое событие"
        assert res_json_result["eventSlug"] == "test-event-slug"
        assert res_json_result["eventDescription"] == "Тестовое описание события"
        assert res_json_result["dateTime"]
        assert res_json_result["groupStatusUntil"]
        assert res_json_result["groupStatusAfter"]
        assert res_json_result["taskNameUntil"]
        assert res_json_result["taskNameAfter"]
        assert res_json_result["eventStatusUntil"]
        assert res_json_result["eventStatusAfter"]
