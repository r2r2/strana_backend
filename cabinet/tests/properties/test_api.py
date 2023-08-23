from http import HTTPStatus
from unittest.mock import AsyncMock, patch

import pytest


# All test coroutines will be treated as marked.
pytestmark = pytest.mark.asyncio


class TestListPropertyTypesEndpoint:
    async def test_property_types_success(self, async_client):
        res = await async_client.get("/properties/types")
        assert res.status_code == 200
        assert res.json() == [
            {"label": "Квартира", "value": "FLAT"},
            {"label": "Паркинг", "value": "PARKING"},
            {"label": "Коммерция", "value": "COMMERCIAL"},
            {"label": "Кладовка", "value": "PANTRY"},
            {"label": "Апартаменты коммерции", "value": "COMMERCIAL_APARTMENT"},
        ]


class TestPropertyBindApi:
    async def test_bind_property_bind_422(self, async_client, property_repo, user_authorization):
        headers = {"Authorization": user_authorization}

        response = await async_client.patch("/properties/bind", headers=headers)
        assert response.status_code == 422


class TestPropertyUnbindApi:
    @pytest.mark.parametrize("payload", [{"booking_id": 1}])
    async def test_unbind_booking_property(
        self,
        booking,
        user_authorization,
        async_client,
        payload,
    ):
        with patch("src.booking.services.deactivate_booking.DeactivateBookingService.__call__",
                   new_callable=AsyncMock) as mock_deactivate_booking_service:
            with patch("src.properties.use_cases.unbind_booking.UpdateTaskInstanceStatusService.__call__",
                       new_callable=AsyncMock) as mock_update_status_service:

                headers = {"Authorization": user_authorization}
                response = await async_client.patch(
                    "/properties/unbind",
                    json=payload,
                    headers=headers,
                )
                assert response.status_code == HTTPStatus.OK
                mock_deactivate_booking_service.assert_called()
                mock_update_status_service.assert_called()
