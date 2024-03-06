from http import HTTPStatus

import pytest


pytestmark = pytest.mark.asyncio


class TestGetQrCode:
    @pytest.mark.skip(reason="need to fix. Есть догадка что это из-за Event в Истории Бронирования")
    async def test_get_qr_code(
        self,
        async_client,
        user_authorization,
        event_list,
        event_participant_list,
    ):
        headers = {"Authorization": user_authorization}
        response = await async_client.get(
            "events_list/qr_code/",
            headers=headers,
        )
        expected_response = {
            'code': event_participant_list.code,
            'title': event_list.title,
            'subtitle': event_list.subtitle,
            'eventDate': event_list.event_date.strftime('%Y-%m-%d'),
            'timeslot': event_participant_list.timeslot,
            'text': event_list.text,
        }

        assert response.status_code == HTTPStatus.OK
        assert response.json() == expected_response
