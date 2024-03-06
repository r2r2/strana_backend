import pytest
from unittest.mock import patch, AsyncMock
from starlette.background import BackgroundTasks

from src.booking.api.booking import _amocrm_status_view
from src.booking.repos import Booking
from src.amocrm.repos import AmocrmStatus
from src.booking.types import WebhookLead, CustomFieldValue

pytestmark = pytest.mark.asyncio


class TestAmoCrmStatusBooking:
    secret = "secret"

    @patch("src.booking.use_cases.amocrm_status_booking.AmoStatusBookingCase._parse_data")
    @patch("src.booking.services.booking_creation.BookingCreationFromAmoService.__call__",
           new_callable=AsyncMock)
    @patch("src.booking.use_cases.amocrm_status_booking.AmoStatusBookingCase._get_booking_creation_status",
           new_callable=AsyncMock)
    @patch("src.meetings.services.import_meeting_from_amo.ImportMeetingFromAmoService.__call__",
           new_callable=AsyncMock)
    async def test_amocrm_status_booking_exists(
        self,
        mock_import_meeting_service,
        mock_get_booking_creation_status,
        mock_booking_creation_from_amo_service,
        mock_parse_data,
        user,
    ):
        """Тест без существующей сделки"""
        payload = b""
        lead = WebhookLead(
            lead_id=32294292,
            pipeline_id=3934218,
            new_status_id=55148413,
            custom_fields={
                596489: CustomFieldValue(name='Объект', value='1318551', enum=1318551),
                643043: CustomFieldValue(name='Дата окончания резерва', value='2024-01-20 00:00:00', enum=None),
            },
            tags={708334: 'Тестовая бронь'}
        )

        mock_import_meeting_service.return_value = None
        mock_parse_data.return_value = lead
        mock_get_booking_creation_status.return_value = AmocrmStatus(name="Бронь")
        mock_booking_creation_from_amo_service.return_value = Booking(id="1111")

        await _amocrm_status_view(payload, background_tasks=BackgroundTasks())

        mock_parse_data.assert_called()
        # mock_import_meeting_service.assert_called()
        mock_booking_creation_from_amo_service.assert_called()

    @patch("src.booking.use_cases.amocrm_status_booking.AmoStatusBookingCase._parse_data")
    @patch("src.booking.services.booking_creation.BookingCreationFromAmoService.__call__",
           new_callable=AsyncMock)
    @patch("src.booking.use_cases.amocrm_status_booking.AmoStatusBookingCase._get_booking_creation_status",
           new_callable=AsyncMock)
    @patch("src.meetings.services.import_meeting_from_amo.ImportMeetingFromAmoService.__call__",
           new_callable=AsyncMock)
    async def test_amocrm_status_booking_not_exists(
        self,
        mock_import_meeting_service,
        mock_get_booking_creation_status,
        mock_booking_creation_from_amo_service,
        mock_parse_data,
        user,
    ):
        """Тест с существующей сделкой"""
        payload = b""
        lead = WebhookLead(
            lead_id=32294292,
            pipeline_id=3934218,
            new_status_id=55148413,
            custom_fields={
                596489: CustomFieldValue(name='Объект', value='1318551', enum=1318551),
                643043: CustomFieldValue(name='Дата окончания резерва', value='2024-01-20 00:00:00', enum=None),
            },
            tags={708334: 'Тестовая бронь'}
        )

        mock_import_meeting_service.return_value = None
        mock_parse_data.return_value = lead
        mock_get_booking_creation_status.return_value = AmocrmStatus(name="Бронь")
        mock_booking_creation_from_amo_service.return_value = None

        await _amocrm_status_view(payload, background_tasks=BackgroundTasks())

        mock_parse_data.assert_called()
        mock_import_meeting_service.assert_called()
        mock_booking_creation_from_amo_service.assert_called()

    @patch("src.booking.use_cases.amocrm_status_booking.AmoStatusBookingCase._parse_data")
    @patch("src.booking.services.booking_creation.BookingCreationFromAmoService.__call__",
           new_callable=AsyncMock)
    @patch("src.booking.use_cases.amocrm_status_booking.AmoStatusBookingCase._get_booking_creation_status",
           new_callable=AsyncMock)
    @patch("src.booking.use_cases.amocrm_status_booking.AmoStatusBookingCase._get_user",
           new_callable=AsyncMock)
    @patch("src.meetings.services.import_meeting_from_amo.ImportMeetingFromAmoService.__call__",
           new_callable=AsyncMock)
    async def test_amocrm_status_booking_not_exists_with_user(
        self,
        mock_import_meeting_service,
        mock_user,
        mock_get_booking_creation_status,
        mock_booking_creation_from_amo_service,
        mock_parse_data,
        user,
    ):
        """Тест с существующей сделкой и с существующим пользователем"""
        payload = b""
        lead = WebhookLead(
            lead_id=32294292,
            pipeline_id=3934218,
            new_status_id=55148413,
            custom_fields={
                596489: CustomFieldValue(name='Объект', value='1318551', enum=1318551),
                643043: CustomFieldValue(name='Дата окончания резерва', value='2024-01-20 00:00:00', enum=None),
            },
            tags={708334: 'Тестовая бронь'}
        )

        mock_import_meeting_service.return_value = None
        mock_parse_data.return_value = lead
        mock_get_booking_creation_status.return_value = AmocrmStatus(name="Бронь")
        mock_booking_creation_from_amo_service.return_value = None
        mock_user.return_value = user

        await _amocrm_status_view(payload, background_tasks=BackgroundTasks())

        mock_parse_data.assert_called()
        mock_import_meeting_service.assert_called()
        mock_booking_creation_from_amo_service.assert_called()
