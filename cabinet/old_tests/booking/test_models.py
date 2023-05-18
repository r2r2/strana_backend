from json import dumps
from pytest import mark

from src.booking.repos import Booking, BookingRepo


@mark.asyncio
class TestBookingModel(object):
    async def _get_booking(
        self, mocker, client, user_authorization, property_repo, property, booking_repo
    ) -> Booking:
        mocker.patch("src.booking.api.booking.tasks.check_booking_task")
        mocker.patch("src.booking.api.booking.tasks.create_booking_log_task")
        mocker.patch("src.booking.api.booking.profitbase.ProfitBase._refresh_auth")
        mocker.patch("src.booking.api.booking.use_cases.AcceptContractCase._backend_booking")
        profitbase_mock = mocker.patch("src.booking.api.booking.profitbase.ProfitBase.get_property")
        profitbase_mock.return_value = {"status": "AVAILABLE"}

        payload = {"property_id": property.id, "contract_accepted": True, "booking_type_id": 1}
        headers = {"Authorization": user_authorization}

        response = await client.post("/booking/accept", data=dumps(payload), headers=headers)
        response_json = response.json()
        response_id = response_json["id"]

        return await booking_repo.retrieve({"id": response_id, "active": True})

    async def test_bulk_update(
        self,
        mocker,
        client,
        user_authorization,
        property_repo,
        property,
        booking_repo: BookingRepo,
    ):
        """Просто тест bulk update."""
        booking = await self._get_booking(
            mocker, client, user_authorization, property_repo, property, booking_repo
        )
        assert booking.active is True
        booking = await booking_repo.update(booking, dict(amocrm_id=123))

        bookings_not_found_in_amocrm = {booking.id}
        filters = dict(id__in=bookings_not_found_in_amocrm, amocrm_id__not_isnull=True)
        data = dict(active=False, deleted_in_amo=True)
        await booking_repo.bulk_update(data=data, filters=filters)

        await booking.refresh_from_db()
        assert booking.active is False
        assert booking.deleted_in_amo is True
