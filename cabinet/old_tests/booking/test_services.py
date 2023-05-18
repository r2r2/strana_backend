import re
from datetime import datetime, timedelta
from typing import Type

from pytest import mark
from pytz import UTC

from src.booking.repos import Booking, BookingRepo
from src.booking.services import DeactivateExpiredBookingsService
from src.properties.repos import PropertyRepo
from src.users.repos import User


@mark.asyncio
class TestCheckBookingService(object):
    async def test_booking_finished(
        self,
        client,
        user,
        mocker,
        booking,
        amocrm_class,
        booking_repo,
        property_repo,
        backend_config,
        profitbase_class,
        graphql_request_class,
        check_booking_service_class,
    ):
        update_data = {
            "should_be_deactivated_by_timer": True,
            "phone_submitted": True,
            "contract_accepted": True,
            "personal_filled": True,
            "params_checked": True,
            "price_payed": True,
            "user_id": user.id,
        }
        await booking_repo.update(booking, update_data)

        settings_mock = mocker.patch("src.booking.tasks.amocrm.AmoCRM._fetch_settings")
        amocrm_mock = mocker.patch("src.booking.tasks.amocrm.AmoCRM.update_lead")

        settings_mock.return_value = {"refresh_token": "test", "access_token": "test"}
        amocrm_mock.return_value = [{"id": 123}]

        check_booking = check_booking_service_class(
            amocrm_class=amocrm_class,
            booking_repo=booking_repo.__class__,
            property_repo=property_repo.__class__,
            backend_config=backend_config,
            profitbase_class=profitbase_class,
            request_class=graphql_request_class,
        )

        await check_booking(booking_id=booking.id)

        updated_booking = await booking_repo.retrieve({"id": booking.id, "active": True})

        assert updated_booking.active is True

    async def test_booking_unfinished(
        self,
        client,
        user,
        mocker,
        booking,
        amocrm_class,
        booking_repo,
        property_repo,
        backend_config,
        profitbase_class,
        graphql_request_class,
        check_booking_service_class,
        booking_backend_data_response,
    ):
        update_data = {
            "should_be_deactivated_by_timer": True,
            "phone_submitted": True,
            "contract_accepted": True,
            "personal_filled": True,
            "params_checked": False,
            "user_id": user.id,
        }
        await booking_repo.update(booking, update_data)

        mocker.patch("src.booking.tasks.requests.GraphQLRequest.__aexit__")
        mocker.patch("src.booking.tasks.profitbase.ProfitBase._refresh_auth")

        settings_mock = mocker.patch("src.booking.tasks.amocrm.AmoCRM._fetch_settings")
        amocrm_mock = mocker.patch("src.booking.tasks.amocrm.AmoCRM.update_lead")
        profitbase_mock = mocker.patch("src.booking.tasks.profitbase.ProfitBase.unbook_property")
        request_mock = mocker.patch("src.booking.tasks.requests.GraphQLRequest.__aenter__")

        settings_mock.return_value = {"refresh_token": "test", "access_token": "test"}
        amocrm_mock.return_value = [{"id": 123}]
        profitbase_mock.return_value = {"success": True}
        request_mock.return_value = booking_backend_data_response

        check_booking = check_booking_service_class(
            amocrm_class=amocrm_class,
            booking_repo=booking_repo.__class__,
            property_repo=property_repo.__class__,
            backend_config=backend_config,
            profitbase_class=profitbase_class,
            request_class=graphql_request_class,
        )

        await check_booking(booking_id=booking.id)

        updated_booking = await booking_repo.retrieve({"id": booking.id})

        assert updated_booking.should_be_deactivated_by_timer is False
        assert updated_booking.active is False


@mark.asyncio
class TestDeactivateExpiredBookingsService(object):
    async def test_booking_finished_expired(
        self,
        client,
        user: User,
        mocker,
        booking: Booking,
        amocrm_class,
        booking_repo: BookingRepo,
        property_repo: PropertyRepo,
        backend_config,
        profitbase_class,
        graphql_request_class,
        deactivate_expired_bookings_service_class: Type[DeactivateExpiredBookingsService],
        booking_backend_data_response,
    ):
        """Нельзя деактивировать по таймеру оплаченные бронирования.

        Бронирование оплачено; типа просрочено по таймеру.
        """
        update_data = {
            "should_be_deactivated_by_timer": True,
            "phone_submitted": True,
            "contract_accepted": True,
            "personal_filled": True,
            "params_checked": True,
            "price_payed": True,
            "user_id": user.id,
            "expires": datetime.now(tz=UTC) - timedelta(minutes=2),
        }
        await booking_repo.update(booking, update_data)

        mocker.patch("src.booking.tasks.requests.GraphQLRequest.__aexit__")
        mocker.patch("src.booking.tasks.profitbase.ProfitBase._refresh_auth")

        settings_mock = mocker.patch("src.booking.tasks.amocrm.AmoCRM._fetch_settings")
        amocrm_mock = mocker.patch("src.booking.tasks.amocrm.AmoCRM.update_lead")
        profitbase_mock = mocker.patch("src.booking.tasks.profitbase.ProfitBase.unbook_property")
        request_mock = mocker.patch("src.booking.tasks.requests.GraphQLRequest.__aenter__")

        settings_mock.return_value = {"refresh_token": "test", "access_token": "test"}
        amocrm_mock.return_value = [{"id": 123}]
        profitbase_mock.return_value = {"success": True}
        request_mock.return_value = booking_backend_data_response

        deactivate_expired_bookings = deactivate_expired_bookings_service_class(
            amocrm_class=amocrm_class,
            booking_repo=booking_repo.__class__,
            property_repo=property_repo.__class__,
            backend_config=backend_config,
            profitbase_class=profitbase_class,
            request_class=graphql_request_class,
        )

        assert booking.active is True
        await deactivate_expired_bookings()

        await booking.refresh_from_db()
        assert booking.active is True

        assert booking.should_be_deactivated_by_timer is False

    async def test_booking_finished_not_expired(
        self,
        client,
        user: User,
        mocker,
        booking: Booking,
        amocrm_class,
        booking_repo: BookingRepo,
        property_repo: PropertyRepo,
        backend_config,
        profitbase_class,
        graphql_request_class,
        deactivate_expired_bookings_service_class: Type[DeactivateExpiredBookingsService],
        booking_backend_data_response,
    ):
        """Нельзя деактивировать по таймеру оплаченные бронирования.

        Бронирование оплачено; типа не просрочено по таймеру.
        """
        update_data = {
            "should_be_deactivated_by_timer": True,
            "phone_submitted": True,
            "contract_accepted": True,
            "personal_filled": True,
            "params_checked": True,
            "price_payed": True,
            "user_id": user.id,
            "expires": datetime.now(tz=UTC) + timedelta(minutes=2),
        }
        await booking_repo.update(booking, update_data)

        mocker.patch("src.booking.tasks.requests.GraphQLRequest.__aexit__")
        mocker.patch("src.booking.tasks.profitbase.ProfitBase._refresh_auth")

        settings_mock = mocker.patch("src.booking.tasks.amocrm.AmoCRM._fetch_settings")
        amocrm_mock = mocker.patch("src.booking.tasks.amocrm.AmoCRM.update_lead")
        profitbase_mock = mocker.patch("src.booking.tasks.profitbase.ProfitBase.unbook_property")
        request_mock = mocker.patch("src.booking.tasks.requests.GraphQLRequest.__aenter__")

        settings_mock.return_value = {"refresh_token": "test", "access_token": "test"}
        amocrm_mock.return_value = [{"id": 123}]
        profitbase_mock.return_value = {"success": True}
        request_mock.return_value = booking_backend_data_response

        deactivate_expired_bookings = deactivate_expired_bookings_service_class(
            amocrm_class=amocrm_class,
            booking_repo=booking_repo.__class__,
            property_repo=property_repo.__class__,
            backend_config=backend_config,
            profitbase_class=profitbase_class,
            request_class=graphql_request_class,
        )

        assert booking.active is True
        await deactivate_expired_bookings()

        await booking.refresh_from_db()
        assert booking.active is True

        assert booking.should_be_deactivated_by_timer is False

    async def test_booking_unfinished_expired(
        self,
        client,
        user: User,
        mocker,
        booking: Booking,
        amocrm_class,
        booking_repo: BookingRepo,
        property_repo: PropertyRepo,
        backend_config,
        profitbase_class,
        graphql_request_class,
        deactivate_expired_bookings_service_class: Type[DeactivateExpiredBookingsService],
        booking_backend_data_response,
    ):
        """Деактивируем неоплаченное бронирование, коротое просрочено по таймеру."""
        update_data = {
            "should_be_deactivated_by_timer": True,
            "phone_submitted": True,
            "contract_accepted": True,
            "personal_filled": True,
            "params_checked": False,
            "user_id": user.id,
            "expires": datetime.now(tz=UTC) - timedelta(minutes=2),
        }
        await booking_repo.update(booking, update_data)

        mocker.patch("src.booking.tasks.requests.GraphQLRequest.__aexit__")
        mocker.patch("src.booking.tasks.profitbase.ProfitBase._refresh_auth")

        settings_mock = mocker.patch("src.booking.tasks.amocrm.AmoCRM._fetch_settings")
        amocrm_mock = mocker.patch("src.booking.tasks.amocrm.AmoCRM.update_lead")
        profitbase_mock = mocker.patch("src.booking.tasks.profitbase.ProfitBase.unbook_property")
        request_mock = mocker.patch("src.booking.tasks.requests.GraphQLRequest.__aenter__")

        settings_mock.return_value = {"refresh_token": "test", "access_token": "test"}
        amocrm_mock.return_value = [{"id": 123}]
        profitbase_mock.return_value = {"success": True}
        request_mock.return_value = booking_backend_data_response

        deactivate_expired_bookings = deactivate_expired_bookings_service_class(
            amocrm_class=amocrm_class,
            booking_repo=booking_repo.__class__,
            property_repo=property_repo.__class__,
            backend_config=backend_config,
            profitbase_class=profitbase_class,
            request_class=graphql_request_class,
        )

        assert booking.active is True
        await deactivate_expired_bookings()

        await booking.refresh_from_db()
        assert booking.active is False

        assert booking.should_be_deactivated_by_timer is False

    async def test_booking_unfinished_not_expired(
        self,
        client,
        user: User,
        mocker,
        booking: Booking,
        amocrm_class,
        booking_repo: BookingRepo,
        property_repo: PropertyRepo,
        backend_config,
        profitbase_class,
        graphql_request_class,
        deactivate_expired_bookings_service_class: Type[DeactivateExpiredBookingsService],
        booking_backend_data_response,
    ):
        """Не деактивируем неоплаченное бронирование, коротое не просрочено по таймеру."""
        update_data = {
            "should_be_deactivated_by_timer": True,
            "phone_submitted": True,
            "contract_accepted": True,
            "personal_filled": True,
            "params_checked": False,
            "user_id": user.id,
            "expires": datetime.now(tz=UTC) + timedelta(minutes=2),
        }
        await booking_repo.update(booking, update_data)

        mocker.patch("src.booking.tasks.requests.GraphQLRequest.__aexit__")
        mocker.patch("src.booking.tasks.profitbase.ProfitBase._refresh_auth")

        settings_mock = mocker.patch("src.booking.tasks.amocrm.AmoCRM._fetch_settings")
        amocrm_mock = mocker.patch("src.booking.tasks.amocrm.AmoCRM.update_lead")
        profitbase_mock = mocker.patch("src.booking.tasks.profitbase.ProfitBase.unbook_property")
        request_mock = mocker.patch("src.booking.tasks.requests.GraphQLRequest.__aenter__")

        settings_mock.return_value = {"refresh_token": "test", "access_token": "test"}
        amocrm_mock.return_value = [{"id": 123}]
        profitbase_mock.return_value = {"success": True}
        request_mock.return_value = booking_backend_data_response

        deactivate_expired_bookings = deactivate_expired_bookings_service_class(
            amocrm_class=amocrm_class,
            booking_repo=booking_repo.__class__,
            property_repo=property_repo.__class__,
            backend_config=backend_config,
            profitbase_class=profitbase_class,
            request_class=graphql_request_class,
        )

        assert booking.active is True
        await deactivate_expired_bookings()

        await booking.refresh_from_db()
        assert booking.active is True

        assert booking.should_be_deactivated_by_timer is True


@mark.asyncio
class TestImportBookingsService(object):
    async def test_success(
        self,
        client,
        user,
        mocker,
        user_types,
        user_repo,
        agent_repo,
        floor_repo,
        amocrm_class,
        project_repo,
        booking_repo,
        building_repo,
        property_repo,
        property_data,
        backend_config,
        global_id_encoder,
        graphql_request_class,
        import_bookings_service_class,
        booking_backend_data_response,
    ):
        update_date = {"amocrm_id": 2281488}
        await user_repo.update(user, update_date)

        lead_mock = mocker.patch("src.booking.tasks.amocrm.AmoCRM.fetch_lead")
        leads_mock = mocker.patch("src.booking.tasks.amocrm.AmoCRM.fetch_leads")
        fetch_mock = mocker.patch("src.booking.tasks.amocrm.AmoCRM.fetch_contact")
        request_mock = mocker.patch("src.booking.tasks.requests.GraphQLRequest.__call__")
        settings_mock = mocker.patch("src.booking.tasks.amocrm.AmoCRM._fetch_settings")

        property_response = booking_backend_data_response
        property_response.data = property_data

        request_mock.return_value = property_response
        settings_mock.return_value = {"refresh_token": "test", "access_token": "test"}
        fetch_mock.return_value = [
            {
                "id": 2281488,
                "pipeline_id": 1941865,
                "created_at": 1000000,
                "updated_at": 1000000,
                "leads": {"id": [100]},
            }
        ]
        leads_mock.return_value = [
            {
                "id": 100,
                "pipeline_id": 1941865,
                "status_id": amocrm_class.msk_status_ids["booking"],
                "is_deleted": False,
                "created_at": 1000000,
                "custom_fields": [
                    {"id": amocrm_class.property_field_id, "values": [{"value": 12345}]},
                    {
                        "id": amocrm_class.property_type_field_id,
                        "values": [amocrm_class.property_type_field_values["flat"]],
                    },
                    {"id": amocrm_class.booking_price_field_id, "values": [{"value": 10000}]},
                ],
            }
        ]

        import_bookings = import_bookings_service_class(
            agent_repo=agent_repo.__class__,
            user_types=user_types,
            amocrm_class=amocrm_class,
            backend_config=backend_config,
            user_repo=user_repo.__class__,
            floor_repo=floor_repo.__class__,
            request_class=graphql_request_class,
            global_id_encoder=global_id_encoder,
            booking_repo=booking_repo.__class__,
            project_repo=project_repo.__class__,
            building_repo=building_repo.__class__,
            property_repo=property_repo.__class__,
        )

        await import_bookings(user.id)

        booking = await booking_repo.retrieve({"amocrm_id": 100})

        awaitable_amocrm_id = 100
        awaitable_payment_amount = 10000

        assert booking.floor_id
        assert booking.project_id
        assert booking.property_id
        assert booking.building_id
        assert booking.user_id == user.id
        assert booking.amocrm_id == awaitable_amocrm_id
        assert int(booking.payment_amount) == awaitable_payment_amount

    async def test_wrong_pipeline_id(
        self,
        client,
        user,
        mocker,
        user_types,
        user_repo,
        agent_repo,
        floor_repo,
        amocrm_class,
        project_repo,
        booking_repo,
        building_repo,
        property_repo,
        property_data,
        backend_config,
        global_id_encoder,
        graphql_request_class,
        import_bookings_service_class,
        booking_backend_data_response,
    ):
        update_date = {"amocrm_id": 2281488}
        await user_repo.update(user, update_date)

        lead_mock = mocker.patch("src.booking.tasks.amocrm.AmoCRM.fetch_lead")
        leads_mock = mocker.patch("src.booking.tasks.amocrm.AmoCRM.fetch_leads")
        fetch_mock = mocker.patch("src.booking.tasks.amocrm.AmoCRM.fetch_contact")
        request_mock = mocker.patch("src.booking.tasks.requests.GraphQLRequest.__call__")
        settings_mock = mocker.patch("src.booking.tasks.amocrm.AmoCRM._fetch_settings")

        property_response = booking_backend_data_response
        property_response.data = property_data

        request_mock.return_value = property_response
        settings_mock.return_value = {"refresh_token": "test", "access_token": "test"}
        fetch_mock.return_value = [
            {
                "id": 2281488,
                "pipeline_id": 1,
                "created_at": 1000000,
                "updated_at": 1000000,
                "leads": {"id": [100]},
            }
        ]
        leads_mock.return_value = [
            {
                "id": 100,
                "pipeline_id": 1,
                "status_id": amocrm_class.msk_status_ids["booking"],
                "is_deleted": False,
                "created_at": 1000000,
                "custom_fields": [
                    {"id": amocrm_class.property_field_id, "values": [{"value": 12345}]},
                    {
                        "id": amocrm_class.property_type_field_id,
                        "values": [amocrm_class.property_type_field_values["flat"]],
                    },
                    {"id": amocrm_class.booking_price_field_id, "values": [{"value": 10000}]},
                ],
            }
        ]

        import_bookings = import_bookings_service_class(
            agent_repo=agent_repo.__class__,
            user_types=user_types,
            amocrm_class=amocrm_class,
            backend_config=backend_config,
            user_repo=user_repo.__class__,
            floor_repo=floor_repo.__class__,
            request_class=graphql_request_class,
            global_id_encoder=global_id_encoder,
            booking_repo=booking_repo.__class__,
            project_repo=project_repo.__class__,
            building_repo=building_repo.__class__,
            property_repo=property_repo.__class__,
        )

        await import_bookings(user.id)

        booking = await booking_repo.retrieve({"amocrm_id": 100})
        assert booking is None


@mark.asyncio
class TestUpdateBookingsServices(object):
    async def test_success(
        self,
        update_bookings_service_class,
        client,
        user,
        mocker,
        user_types,
        user_repo,
        agent_repo,
        floor_repo,
        amocrm_class,
        project_repo,
        booking_repo,
        building_repo,
        property_repo,
        property_data,
        backend_config,
        global_id_encoder,
        graphql_request_class,
        import_bookings_service_class,
        booking_backend_data_response,
        booking,
    ):
        amocrm_id = 112233
        await booking_repo.update(booking, {"amocrm_id": amocrm_id})

        settings_mock = mocker.patch("src.booking.tasks.amocrm.AmoCRM._fetch_settings")
        request_mock = mocker.patch("src.booking.tasks.requests.GraphQLRequest.__call__")
        property_response = booking_backend_data_response
        property_response.data = property_data

        request_mock.return_value = property_response
        leads_mock = mocker.patch("src.booking.tasks.amocrm.AmoCRM.fetch_leads")
        leads_mock.return_value = [
            {
                "id": amocrm_id,
                "pipeline_id": 1941865,
                "status_id": amocrm_class.msk_status_ids["booking"],
                "is_deleted": False,
                "created_at": 1000000,
                "custom_fields": [
                    {"id": amocrm_class.property_field_id, "values": [{"value": 1}]},
                    {
                        "id": amocrm_class.property_type_field_id,
                        "values": [amocrm_class.property_type_field_values["flat"]],
                    },
                    {"id": amocrm_class.booking_price_field_id, "values": [{"value": 10000}]},
                ],
            }
        ]

        update_bookings = update_bookings_service_class(
            booking_repo=booking_repo.__class__,
            amocrm_class=amocrm_class,
            global_id_encoder=global_id_encoder,
            property_repo=property_repo.__class__,
            backend_config=backend_config,
            request_class=graphql_request_class,
            project_repo=project_repo.__class__,
            floor_repo=floor_repo.__class__,
            building_repo=building_repo.__class__,
        )
        await update_bookings()

        booking = await booking_repo.retrieve({"amocrm_id": amocrm_id})
        assert booking.amocrm_stage == "booking"
        assert booking.amocrm_substage == "booking"
        assert booking.active
        assert booking.property_id == 1

    async def test_wrong_pipeline_id(
        self,
        update_bookings_service_class,
        client,
        user,
        mocker,
        user_types,
        user_repo,
        agent_repo,
        floor_repo,
        amocrm_class,
        project_repo,
        booking_repo,
        building_repo,
        property_repo,
        property_data,
        backend_config,
        global_id_encoder,
        graphql_request_class,
        import_bookings_service_class,
        booking_backend_data_response,
        booking,
    ):
        amocrm_id = 112233
        await booking_repo.update(booking, {"amocrm_id": amocrm_id})

        settings_mock = mocker.patch("src.booking.tasks.amocrm.AmoCRM._fetch_settings")
        request_mock = mocker.patch("src.booking.tasks.requests.GraphQLRequest.__call__")
        property_response = booking_backend_data_response
        property_response.data = property_data

        request_mock.return_value = property_response
        leads_mock = mocker.patch("src.booking.tasks.amocrm.AmoCRM.fetch_leads")
        leads_mock.return_value = [
            {
                "id": amocrm_id,
                "pipeline_id": 1,
                "status_id": amocrm_class.msk_status_ids["booking"],
                "is_deleted": False,
                "created_at": 1000000,
                "custom_fields": [
                    {"id": amocrm_class.property_field_id, "values": [{"value": 1}]},
                    {
                        "id": amocrm_class.property_type_field_id,
                        "values": [amocrm_class.property_type_field_values["flat"]],
                    },
                    {"id": amocrm_class.booking_price_field_id, "values": [{"value": 10000}]},
                ],
            }
        ]

        update_bookings = update_bookings_service_class(
            booking_repo=booking_repo.__class__,
            amocrm_class=amocrm_class,
            global_id_encoder=global_id_encoder,
            property_repo=property_repo.__class__,
            backend_config=backend_config,
            request_class=graphql_request_class,
            project_repo=project_repo.__class__,
            floor_repo=floor_repo.__class__,
            building_repo=building_repo.__class__,
        )
        await update_bookings()

        booking = await booking_repo.retrieve({"amocrm_id": amocrm_id})
        assert not booking.active


@mark.asyncio
class TestGenerateOnlinePurchaseIDService(object):
    async def test_generate_online_purchase_id(
        self, client, generate_online_purchase_id_service
    ) -> None:
        online_purchase_id: str = await generate_online_purchase_id_service()

        regex_pattern = "^[0-9]{2}-[A-Z]{2}-[0-9]{3}$"
        match = re.match(regex_pattern, online_purchase_id)
        assert match is not None
