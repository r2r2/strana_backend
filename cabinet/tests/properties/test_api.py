import datetime
from http import HTTPStatus
from unittest.mock import AsyncMock, patch, call

import pytest
from pytz import UTC

from src.booking.constants import BookingCreatedSources, BookingSubstages
from src.properties.use_cases.bind_booking import BindBookingPropertyCase
from src.task_management.constants import PaidBookingSlug


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

    async def test_bind_booking_property_booked_400(
            self,
            async_client,
            user_authorization,
            bind_booking,
            booked_property,
            building_booking_type,
    ):
        payload = dict(
            property_id=booked_property.id,
            booking_id=bind_booking.id,
            booking_type_id=building_booking_type.id,
        )
        headers = {"Authorization": user_authorization}
        response = await async_client.patch(
            "/properties/bind",
            json=payload,
            headers=headers,
        )

        assert response.status_code == HTTPStatus.BAD_REQUEST
        assert response.json()["reason"] == "booking_property_missing"

    @patch("src.properties.services.check_profitbase_property.CheckProfitbasePropertyService.__call__",
           new_callable=AsyncMock)
    async def test_bind_booking_property_not_available_in_profit_400(
            self,
            mock_check_profitbase_property_service,
            async_client,
            user_authorization,
            bind_booking,
            property,
            building_booking_type,
    ):
        mock_check_profitbase_property_service.return_value = 0, False

        payload = dict(
            property_id=property.id,
            booking_id=bind_booking.id,
            booking_type_id=building_booking_type.id,
        )
        headers = {"Authorization": user_authorization}
        response = await async_client.patch(
            "/properties/bind",
            json=payload,
            headers=headers,
        )

        assert response.status_code == HTTPStatus.BAD_REQUEST
        assert response.json()["reason"] == "booking_property_unavailable"
        mock_check_profitbase_property_service.assert_called_once_with(property)

    @patch("src.properties.services.check_profitbase_property.CheckProfitbasePropertyService.__call__",
           new_callable=AsyncMock)
    async def test_bind_booking_property_booked_in_profit_400(
            self,
            mock_check_profitbase_property_service,
            async_client,
            user_authorization,
            bind_booking,
            property,
            building_booking_type,
    ):
        mock_check_profitbase_property_service.return_value = 1, True

        payload = dict(
            property_id=property.id,
            booking_id=bind_booking.id,
            booking_type_id=building_booking_type.id,
        )
        headers = {"Authorization": user_authorization}
        response = await async_client.patch(
            "/properties/bind",
            json=payload,
            headers=headers,
        )

        assert response.status_code == HTTPStatus.BAD_REQUEST
        assert response.json()["reason"] == "booking_property_unavailable"
        mock_check_profitbase_property_service.assert_called_once_with(property)

    @patch("src.properties.services.check_profitbase_property.CheckProfitbasePropertyService.__call__",
           new_callable=AsyncMock)
    @patch("common.unleash.client.UnleashClient.is_enabled")
    @patch("common.amocrm.amocrm.AmoCRM.__ainit__", new_callable=AsyncMock)
    @patch("common.amocrm.amocrm.AmoCRM.__aexit__", new_callable=AsyncMock)
    @patch("common.amocrm.components.leads.AmoCRMLeads.update_lead_v4", new_callable=AsyncMock)
    @patch("common.utils.from_global_id")
    @patch("src.booking.services.activate_booking.ActivateBookingService.__call__", new_callable=AsyncMock)
    @patch("src.users.services.check_pinning_status.CheckPinningStatusServiceV2.as_task")
    @patch("src.properties.use_cases.bind_booking.BindBookingPropertyCase._create_task_instance",
           new_callable=AsyncMock)
    @patch("src.booking.repos.booking.Booking.is_agent_assigned")
    @patch("src.properties.use_cases.bind_booking.BindBookingPropertyCase.update_task_instance_status",
           new_callable=AsyncMock)
    @patch("src.properties.use_cases.bind_booking.BindBookingPropertyCase._send_sms",
           new_callable=AsyncMock)
    @patch("src.booking.services.send_sms_msk_client.SendSmsToMskClientService.__call__",
           new_callable=AsyncMock)
    async def test_bind_booking_property_by_reservation_matrix(
            self,
            mock_send_sms_msk_client_service,
            mock_send_sms_service,
            mock_update_task_instance_service,
            mock_booking_is_agent_assigned,
            mock_create_task_instance_service,
            mock_check_pinning_status_service,
            mock_activate_booking_service,
            mock_from_global_id,
            mock_amocrm_update_lead_v4,
            mock_amocrm_aexit,
            mock_amocrm_ainit,
            mock_unleash_client,
            mock_check_profitbase_property_service,
            async_client,
            user_authorization,
            booking_repo,
            bind_booking,
            property,
            bind_amo_status,
            building_booking_type,
            booking_reservation_matrix_repo,
            booking_reservation_matrix_amo,
    ):
        mock_unleash_client.return_value = False
        mock_check_profitbase_property_service.return_value = 0, True

        payload = dict(
            property_id=property.id,
            booking_id=bind_booking.id,
            booking_type_id=building_booking_type.id,
        )
        headers = {"Authorization": user_authorization}
        response = await async_client.patch(
            "/properties/bind",
            json=payload,
            headers=headers,
        )

        # получаем данные из тестовой БД для проверки
        booking_reservation_matrix = await booking_reservation_matrix_repo.retrieve(
            filters=dict(created_source=BookingCreatedSources.AMOCRM)
        )

        # общий ответ апи
        assert response.status_code == HTTPStatus.OK
        assert response.json()["expires"]
        # проверка матрицы резервирования
        assert (datetime.datetime.fromisoformat(response.json()["expires"]) - datetime.datetime.now(tz=UTC)) < \
               datetime.timedelta(hours=booking_reservation_matrix.reservation_time)
        assert (datetime.datetime.fromisoformat(response.json()["expires"]) - datetime.datetime.now(tz=UTC)) > \
               datetime.timedelta(hours=booking_reservation_matrix.reservation_time) - datetime.timedelta(seconds=5)

    @patch("src.properties.services.check_profitbase_property.CheckProfitbasePropertyService.__call__",
           new_callable=AsyncMock)
    @patch("common.unleash.client.UnleashClient.is_enabled")
    @patch("common.amocrm.amocrm.AmoCRM.__ainit__", new_callable=AsyncMock)
    @patch("common.amocrm.amocrm.AmoCRM.__aexit__", new_callable=AsyncMock)
    @patch("common.amocrm.components.leads.AmoCRMLeads.update_lead_v4", new_callable=AsyncMock)
    @patch("common.utils.from_global_id")
    @patch("src.booking.services.activate_booking.ActivateBookingService.__call__", new_callable=AsyncMock)
    @patch("src.users.services.check_pinning_status.CheckPinningStatusServiceV2.as_task")
    @patch("src.properties.use_cases.bind_booking.BindBookingPropertyCase._create_task_instance",
           new_callable=AsyncMock)
    @patch("src.booking.repos.booking.Booking.is_agent_assigned")
    @patch("src.properties.use_cases.bind_booking.BindBookingPropertyCase.update_task_instance_status",
           new_callable=AsyncMock)
    @patch("src.properties.use_cases.bind_booking.BindBookingPropertyCase._send_sms",
           new_callable=AsyncMock)
    @patch("src.booking.services.send_sms_msk_client.SendSmsToMskClientService.__call__",
           new_callable=AsyncMock)
    async def test_bind_booking_property_by_booking_settings(
            self,
            mock_send_sms_msk_client_service,
            mock_send_sms_service,
            mock_update_task_instance_service,
            mock_booking_is_agent_assigned,
            mock_create_task_instance_service,
            mock_check_pinning_status_service,
            mock_activate_booking_service,
            mock_from_global_id,
            mock_amocrm_update_lead_v4,
            mock_amocrm_aexit,
            mock_amocrm_ainit,
            mock_unleash_client,
            mock_check_profitbase_property_service,
            async_client,
            user_authorization,
            bind_booking,
            property,
            bind_amo_status,
            building_booking_type,
            booking_reservation_matrix_repo,
            booking_reservation_matrix_lk,
            booking_settings_repo,
            booking_settings,
    ):
        mock_unleash_client.return_value = False
        mock_check_profitbase_property_service.return_value = 0, True

        payload = dict(
            property_id=property.id,
            booking_id=bind_booking.id,
            booking_type_id=building_booking_type.id,
        )
        headers = {"Authorization": user_authorization}
        response = await async_client.patch(
            "/properties/bind",
            json=payload,
            headers=headers,
        )

        # получаем данные из тестовой БД для проверки
        booking_settings = await booking_settings_repo.list().first()

        # общий ответ апи
        assert response.status_code == HTTPStatus.OK
        assert response.json()["expires"]
        # проверка стандартных настроек бронирований для времени резервирования
        assert (datetime.datetime.fromisoformat(response.json()["expires"]) - datetime.datetime.now(tz=UTC)) < \
               datetime.timedelta(hours=booking_settings.default_flats_reserv_time)
        assert (datetime.datetime.fromisoformat(response.json()["expires"]) - datetime.datetime.now(tz=UTC)) > \
               datetime.timedelta(hours=booking_settings.default_flats_reserv_time) - datetime.timedelta(seconds=5)

    @patch("src.properties.services.check_profitbase_property.CheckProfitbasePropertyService.__call__",
           new_callable=AsyncMock)
    @patch("common.unleash.client.UnleashClient.is_enabled")
    @patch("common.amocrm.amocrm.AmoCRM.__ainit__", new_callable=AsyncMock)
    @patch("common.amocrm.amocrm.AmoCRM.__aexit__", new_callable=AsyncMock)
    @patch("common.amocrm.components.leads.AmoCRMLeads.update_lead_v4", new_callable=AsyncMock)
    @patch("common.utils.from_global_id")
    @patch("src.booking.services.activate_booking.ActivateBookingService.__call__", new_callable=AsyncMock)
    @patch("src.users.services.check_pinning_status.CheckPinningStatusServiceV2.as_task")
    @patch("src.properties.use_cases.bind_booking.BindBookingPropertyCase._create_task_instance",
           new_callable=AsyncMock)
    @patch("src.booking.repos.booking.Booking.is_agent_assigned")
    @patch("src.properties.use_cases.bind_booking.BindBookingPropertyCase.update_task_instance_status",
           new_callable=AsyncMock)
    @patch("src.properties.use_cases.bind_booking.BindBookingPropertyCase._send_sms",
           new_callable=AsyncMock)
    @patch("src.booking.services.send_sms_msk_client.SendSmsToMskClientService.__call__",
           new_callable=AsyncMock)
    @patch("common.amocrm.components.notes.AmoCRMNotes.send_lead_note",
           new_callable=AsyncMock)
    async def test_bind_booking_property_price(
        self,
        mock_amocrm_send_lead_note,
        mock_send_sms_msk_client_service,
        mock_send_sms_service,
        mock_update_task_instance_service,
        mock_booking_is_agent_assigned,
        mock_create_task_instance_service,
        mock_check_pinning_status_service,
        mock_activate_booking_service,
        mock_from_global_id,
        mock_amocrm_update_lead_v4,
        mock_amocrm_aexit,
        mock_amocrm_ainit,
        mock_unleash_client,
        mock_check_profitbase_property_service,
        booking_repo,
        bind_booking,
        user_authorization,
        async_client,
        property,
        bind_amo_status,
        building_booking_type,
        booking_reservation_matrix_amo,
        payment_method,
        mortgage_type,
        property_offer_matrix,
        property_price,
        faker,
    ):
        mock_unleash_client.return_value = True
        mock_check_profitbase_property_service.return_value = 0, True

        payload = dict(
            property_id=property.id,
            payment_method_slug=payment_method.slug,
            mortgage_type_by_dev=mortgage_type.by_dev,
            mortgage_program_name=faker.text(),
            calculator_options='[1,2,3,{"4":5,"6":7}]',
            booking_id=bind_booking.id,
            booking_type_id=building_booking_type.id,
        )
        headers = {"Authorization": user_authorization}
        response = await async_client.patch(
            "/properties/bind",
            json=payload,
            headers=headers,
        )

        # получаем данные из тестовой БД для проверки
        updated_booking = await booking_repo.retrieve(filters=dict(id=bind_booking.id))

        # общий ответ апи
        assert response.status_code == HTTPStatus.OK
        # проверка получения поля матрицы цены недвижимости
        assert updated_booking.price_id
        assert updated_booking.price_offer_id
        assert updated_booking.amo_payment_method_id
        assert updated_booking.mortgage_type_id
        assert updated_booking.mortgage_offer
        assert updated_booking.calculator_options

        mock_amocrm_send_lead_note.assert_has_calls(
            [
                call(lead_id=bind_booking.amocrm_id, message=f"Выбранные опции - {payload['calculator_options']}"),
                call(
                    lead_id=bind_booking.amocrm_id,
                    message=f"Название ипотечной программы - {payload.get('mortgage_program_name')}",
                )
            ],
            any_order=True,
        )

    @patch("src.properties.services.check_profitbase_property.CheckProfitbasePropertyService.__call__",
           new_callable=AsyncMock)
    @patch("common.unleash.client.UnleashClient.is_enabled")
    @patch("common.amocrm.amocrm.AmoCRM.__ainit__", new_callable=AsyncMock)
    @patch("common.amocrm.amocrm.AmoCRM.__aexit__", new_callable=AsyncMock)
    @patch("common.amocrm.components.leads.AmoCRMLeads.update_lead_v4", new_callable=AsyncMock)
    @patch("common.utils.from_global_id")
    @patch("src.booking.services.activate_booking.ActivateBookingService.__call__", new_callable=AsyncMock)
    @patch("src.users.services.check_pinning_status.CheckPinningStatusServiceV2.as_task")
    @patch("src.properties.use_cases.bind_booking.BindBookingPropertyCase._create_task_instance",
           new_callable=AsyncMock)
    @patch("src.booking.repos.booking.Booking.is_agent_assigned")
    @patch("src.properties.use_cases.bind_booking.BindBookingPropertyCase.update_task_instance_status",
           new_callable=AsyncMock)
    @patch("src.properties.use_cases.bind_booking.BindBookingPropertyCase._send_sms",
           new_callable=AsyncMock)
    @patch("src.booking.services.send_sms_msk_client.SendSmsToMskClientService.__call__",
           new_callable=AsyncMock)
    @patch("common.amocrm.components.notes.AmoCRMNotes.send_lead_note",
           new_callable=AsyncMock)
    async def test_bind_booking_default_property_price(
            self,
            mock_amocrm_send_lead_note,
            mock_send_sms_msk_client_service,
            mock_send_sms_service,
            mock_update_task_instance_service,
            mock_booking_is_agent_assigned,
            mock_create_task_instance_service,
            mock_check_pinning_status_service,
            mock_activate_booking_service,
            mock_from_global_id,
            mock_amocrm_update_lead_v4,
            mock_amocrm_aexit,
            mock_amocrm_ainit,
            mock_unleash_client,
            mock_check_profitbase_property_service,
            booking_repo,
            bind_booking,
            user_authorization,
            async_client,
            property,
            bind_amo_status,
            building_booking_type,
            booking_reservation_matrix_amo,
            property_offer_matrix_default,
            property_price_default,
            faker,
    ):
        mock_unleash_client.return_value = True
        mock_check_profitbase_property_service.return_value = 0, True

        payload = dict(
            property_id=property.id,
            payment_method_slug="heisenberg",
            booking_id=bind_booking.id,
            booking_type_id=building_booking_type.id,
        )
        headers = {"Authorization": user_authorization}
        response = await async_client.patch(
            "/properties/bind",
            json=payload,
            headers=headers,
        )

        # получаем данные из тестовой БД для проверки
        updated_booking = await booking_repo.retrieve(filters=dict(id=bind_booking.id))

        # общий ответ апи
        assert response.status_code == HTTPStatus.OK
        # проверка получения поля матрицы цены недвижимости
        assert updated_booking.price_id
        assert updated_booking.price_offer_id

    @patch("src.properties.services.check_profitbase_property.CheckProfitbasePropertyService.__call__",
           new_callable=AsyncMock)
    @patch("common.unleash.client.UnleashClient.is_enabled")
    @patch("common.amocrm.amocrm.AmoCRM.__ainit__", new_callable=AsyncMock)
    @patch("common.amocrm.amocrm.AmoCRM.__aexit__", new_callable=AsyncMock)
    @patch("common.amocrm.components.leads.AmoCRMLeads.update_lead_v4", new_callable=AsyncMock)
    @patch("common.utils.from_global_id")
    @patch("src.booking.services.activate_booking.ActivateBookingService.__call__", new_callable=AsyncMock)
    @patch("src.users.services.check_pinning_status.CheckPinningStatusServiceV2.as_task")
    @patch("src.properties.use_cases.bind_booking.BindBookingPropertyCase._create_task_instance",
           new_callable=AsyncMock)
    @patch("src.booking.repos.booking.Booking.is_agent_assigned")
    @patch("src.properties.use_cases.bind_booking.BindBookingPropertyCase.update_task_instance_status",
           new_callable=AsyncMock)
    @patch("src.properties.use_cases.bind_booking.BindBookingPropertyCase._send_sms",
           new_callable=AsyncMock)
    @patch("src.booking.services.send_sms_msk_client.SendSmsToMskClientService.__call__",
           new_callable=AsyncMock)
    async def test_bind_booking_property(
            self,
            mock_send_sms_msk_client_service,
            mock_send_sms_service,
            mock_update_task_instance_service,
            mock_booking_is_agent_assigned,
            mock_create_task_instance_service,
            mock_check_pinning_status_service,
            mock_activate_booking_service,
            mock_from_global_id,
            mock_amocrm_update_lead_v4,
            mock_amocrm_aexit,
            mock_amocrm_ainit,
            mock_unleash_client,
            mock_check_profitbase_property_service,
            booking_repo,
            bind_booking,
            user_authorization,
            async_client,
            property,
            bind_amo_status,
            building_booking_type,
            booking_reservation_matrix_amo,
            purchase_amo_matrix_repo,
            purchase_amo_matrix,
    ):
        mock_unleash_client.return_value = False
        mock_check_profitbase_property_service.return_value = 0, True

        payload = dict(
            property_id=property.id,
            booking_id=bind_booking.id,
            booking_type_id=building_booking_type.id,
        )
        headers = {"Authorization": user_authorization}
        response = await async_client.patch(
            "/properties/bind",
            json=payload,
            headers=headers,
        )

        # получаем данные из тестовой БД для проверки
        updated_booking = await booking_repo.retrieve(filters=dict(id=bind_booking.id))
        purchase_amo_matrix = await purchase_amo_matrix_repo.retrieve(
            filters=dict(
                payment_method_id=bind_booking.amo_payment_method_id,
                mortgage_type_id=bind_booking.mortgage_type_id,
            )
        )

        # общий ответ апи
        assert response.status_code == HTTPStatus.OK
        assert response.json()["id"] == bind_booking.id
        assert response.json()["active"] is True
        assert response.json()["propertyId"] == property.id
        assert response.json()["expires"]
        # проверка добавления тегов
        assert BindBookingPropertyCase.TAG in updated_booking.tags
        # поля после выбора типов бронирования
        assert updated_booking.payment_amount
        assert updated_booking.booking_period
        assert updated_booking.until
        # проверка подсчета скидки
        assert updated_booking.final_payment_amount != property.original_price
        # проверка получения поля типа оплаты для экспорта в амо
        assert purchase_amo_matrix

        # проверка вызова замоканых функций/сервисов с сигнатурой
        mock_create_task_instance_service.assert_called_once_with(booking=bind_booking)
        mock_check_pinning_status_service.assert_called_once_with(user_id=bind_booking.user_id)
        mock_activate_booking_service.assert_called_once_with(
            booking=bind_booking,
            amocrm_substage=BookingSubstages.MAKE_DECISION,
        )
        mock_amocrm_update_lead_v4.assert_called_once()
        mock_amocrm_ainit.assert_called_once()
        mock_amocrm_aexit.assert_called_once()
        mock_from_global_id.assert_called_once_with(property.global_id)
        mock_check_profitbase_property_service.assert_called_once_with(property)
        mock_booking_is_agent_assigned.assert_called_once()
        mock_update_task_instance_service.assert_called_once_with(
            booking_id=bind_booking.id,
            status_slug=PaidBookingSlug.WAIT_PAYMENT.value,
        )
        mock_send_sms_service.assert_called_once_with(bind_booking)
        mock_send_sms_msk_client_service.assert_called_once_with(
            booking_id=bind_booking.id,
            sms_slug=BindBookingPropertyCase.sms_event_slug,
        )


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
