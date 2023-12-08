import pytest
from unittest.mock import patch, AsyncMock

from starlette.background import BackgroundTasks

from src.booking.api.booking import _amocrm_webhook_view
from src.booking.repos import Booking
from src.booking.types import WebhookLead, CustomFieldValue

pytestmark = pytest.mark.asyncio


class TestAmoWebhook:
    secret = "secret"

    @patch("src.booking.use_cases.amocrm_webhook.compare_digest")
    async def test__amocrm_webhook_view(
            self,
            mock_compare_digest,
    ):
        payload = b""
        background_tasks = BackgroundTasks()
        secret = "secret"

        mock_compare_digest.return_value = True

        await _amocrm_webhook_view(payload, background_tasks, secret)

    @patch("src.booking.use_cases.amocrm_webhook.compare_digest")
    @patch("src.users.services.import_client_from_amo.ImportContactFromAmoService.__call__", new_callable=AsyncMock)
    @patch("src.meetings.services.import_meeting_from_amo.ImportMeetingFromAmoService.__call__",
           new_callable=AsyncMock)
    @patch("common.amocrm.amocrm.AmoCRM.get_lead_substage",)
    async def test_lead_without_custom_fields(
            self,
            mock_get_lead_substage,
            mock_import_meeting_service,
            mock_user,
            mock_compare_digest,
            user,
    ):
        payload = b""
        background_tasks = None
        secret = "secret"

        mock_compare_digest.return_value = True
        mock_user.return_value = user
        mock_import_meeting_service.return_value = None
        mock_get_lead_substage.return_value = "assign_agent"

        await _amocrm_webhook_view(payload, background_tasks, secret)

        mock_compare_digest.assert_called()
        mock_user.assert_called()
        mock_import_meeting_service.assert_called()
        mock_get_lead_substage.assert_not_called()

    @patch("src.booking.use_cases.amocrm_webhook.compare_digest")
    @patch("src.users.services.import_client_from_amo.ImportContactFromAmoService.__call__", new_callable=AsyncMock)
    @patch("src.meetings.services.import_meeting_from_amo.ImportMeetingFromAmoService.__call__",
           new_callable=AsyncMock)
    @patch("common.amocrm.amocrm.AmoCRM.get_lead_substage",)
    @patch("src.booking.use_cases.amocrm_webhook.AmoCRMWebhookCase._parse_data",)
    async def test_lead_with_custom_fields(
            self,
            mock_parse_data,
            mock_get_lead_substage,
            mock_import_meeting_service,
            mock_user,
            mock_compare_digest,
            user,
    ):
        payload = b""
        background_tasks = BackgroundTasks()
        secret = "secret"

        lead = WebhookLead(
            lead_id=32294292,
            pipeline_id=None,
            new_status_id=55148413,
            custom_fields={
                596489: CustomFieldValue(name='Объект', value='1318551', enum=1318551),
                825820: CustomFieldValue(name='0.0.2 Заполняем источник лида', value='1', enum=None)},
            tags={708334: 'Тестовая бронь'}
        )

        mock_compare_digest.return_value = True
        mock_user.return_value = user
        mock_import_meeting_service.return_value = "meeting"
        mock_get_lead_substage.return_value = "assign_agent"
        mock_parse_data.return_value = lead

        await _amocrm_webhook_view(payload, background_tasks, secret)

        mock_compare_digest.assert_called()
        mock_parse_data.assert_called()
        mock_user.assert_called()
        mock_import_meeting_service.assert_called()
        mock_get_lead_substage.assert_called()

    @patch("src.booking.use_cases.amocrm_webhook.compare_digest")
    @patch("src.users.services.import_client_from_amo.ImportContactFromAmoService.__call__", new_callable=AsyncMock)
    @patch("src.meetings.services.import_meeting_from_amo.ImportMeetingFromAmoService.__call__",
           new_callable=AsyncMock)
    @patch("common.amocrm.amocrm.AmoCRM.get_lead_substage",)
    @patch("src.booking.use_cases.amocrm_webhook.AmoCRMWebhookCase._parse_data")
    @patch("src.booking.use_cases.amocrm_webhook.AmoCRMWebhookCase._update_booking_fixation_status",
           new_callable=AsyncMock)
    @patch("src.booking.use_cases.amocrm_webhook.AmoCRMWebhookCase._update_booking_status",
           new_callable=AsyncMock)
    @patch("src.booking.use_cases.amocrm_webhook.AmoCRMWebhookCase._update_booking_custom_fields",
           new_callable=AsyncMock)
    @patch("src.booking.use_cases.amocrm_webhook.AmoCRMWebhookCase._check_user_pinning_status",
           new_callable=AsyncMock)
    @patch("src.booking.loggers.wrappers.booking_changes_logger",  # booking_deactivate
           new_callable=AsyncMock)
    @patch("src.booking.use_cases.amocrm_webhook.AmoCRMWebhookCase._is_stage_valid",
           new_callable=AsyncMock)
    @patch("starlette.background.BackgroundTasks.add_task",
           new_callable=AsyncMock)
    @patch("src.booking.use_cases.amocrm_webhook.AmoCRMWebhookCase._update_meeting_status",
           new_callable=AsyncMock)
    @patch("src.booking.use_cases.amocrm_webhook.AmoCRMWebhookCase.create_task_instance",
           new_callable=AsyncMock)
    async def test_no_update_if_no_booking_and_no_create_status(
            self,
            mock_create_task_instance,
            mock_update_meeting_status,
            mock_add_task,
            mock_is_stage_valid,
            mock_booking_changes_logger,
            mock_check_user_pinning_status,
            mock_update_booking_custom_fields,
            mock_update_booking_status,
            mock_update_booking_fixation_status,
            mock_parse_data,
            mock_get_lead_substage,
            mock_import_meeting_service,
            mock_user,
            mock_compare_digest,
            user,
    ):
        # Case 3
        payload = b""
        background_tasks = BackgroundTasks()
        secret = "secret"

        lead = WebhookLead(
            lead_id=32294292,
            pipeline_id=3934218,
            new_status_id=55148413,
            custom_fields={
                825820: CustomFieldValue(name='0.0.2 Заполняем источник лида', value='1', enum=None)},
            tags={708334: 'Тестовая бронь'}
        )

        mock_compare_digest.return_value = True
        mock_user.return_value = user
        mock_import_meeting_service.return_value = "meeting"
        mock_get_lead_substage.return_value = "assign_agent"
        mock_parse_data.return_value = lead

        await _amocrm_webhook_view(payload, background_tasks, secret)

        mock_compare_digest.assert_called()
        mock_parse_data.assert_called()
        mock_user.assert_called()
        mock_import_meeting_service.assert_called()
        mock_get_lead_substage.assert_called()

        mock_update_booking_custom_fields.assert_not_called()
        mock_update_booking_status.assert_not_called()
        mock_update_booking_fixation_status.assert_not_called()
        mock_check_user_pinning_status.assert_not_called()
        mock_booking_changes_logger.assert_not_called()
        mock_is_stage_valid.assert_not_called()
        mock_add_task.assert_not_called()
        mock_update_meeting_status.assert_not_called()
        mock_create_task_instance.assert_not_called()

    @patch("src.booking.use_cases.amocrm_webhook.compare_digest")
    @patch("src.users.services.import_client_from_amo.ImportContactFromAmoService.__call__", new_callable=AsyncMock)
    @patch("src.meetings.services.import_meeting_from_amo.ImportMeetingFromAmoService.__call__",
           new_callable=AsyncMock)
    @patch("common.amocrm.amocrm.AmoCRM.get_lead_substage",)
    @patch("src.booking.use_cases.amocrm_webhook.AmoCRMWebhookCase._parse_data")
    @patch("src.booking.services.booking_creation.BookingCreationFromAmoService.__call__",
           new_callable=AsyncMock)
    @patch("src.booking.use_cases.amocrm_webhook.AmoCRMWebhookCase._update_booking_fixation_status",
           new_callable=AsyncMock)
    @patch("src.booking.use_cases.amocrm_webhook.AmoCRMWebhookCase._update_booking_status",
           new_callable=AsyncMock)
    @patch("src.booking.use_cases.amocrm_webhook.AmoCRMWebhookCase._update_booking_custom_fields",
           new_callable=AsyncMock)
    @patch("src.booking.use_cases.amocrm_webhook.AmoCRMWebhookCase._check_user_pinning_status",
           new_callable=AsyncMock)
    @patch("src.booking.loggers.wrappers.booking_changes_logger",  # booking_deactivate
           new_callable=AsyncMock)
    @patch("src.booking.use_cases.amocrm_webhook.AmoCRMWebhookCase._is_stage_valid",
           new_callable=AsyncMock)
    @patch("starlette.background.BackgroundTasks.add_task",
           new_callable=AsyncMock)
    @patch("src.booking.use_cases.amocrm_webhook.AmoCRMWebhookCase._update_meeting_status",
           new_callable=AsyncMock)
    @patch("src.booking.use_cases.amocrm_webhook.AmoCRMWebhookCase.create_task_instance",
           new_callable=AsyncMock)
    @patch("src.booking.use_cases.amocrm_webhook.AmoCRMWebhookCase._get_booking_creation_status",
           new_callable=AsyncMock)
    @patch("src.booking.use_cases.amocrm_webhook.AmoCRMWebhookCase._need_deactivate_bookings_task")
    @patch("src.booking.use_cases.amocrm_webhook.AmoCRMWebhookCase._is_different_amocrm_substage")
    async def test_no_booking_and_have_create_status_and_have_booking_expires_datetime_field_id(
            self,
            mock_is_different_amocrm_substage,
            mock_need_deactivate_bookings_task,
            mock_get_booking_creation_status,
            mock_create_task_instance,
            mock_update_meeting_status,
            mock_add_task,
            mock_is_stage_valid,
            mock_booking_changes_logger,
            mock_check_user_pinning_status,
            mock_update_booking_custom_fields,
            mock_update_booking_status,
            mock_update_booking_fixation_status,
            mock_booking_creation_from_amo_service,
            mock_parse_data,
            mock_get_lead_substage,
            mock_import_meeting_service,
            mock_user,
            mock_compare_digest,
            user,
    ):
        # Case 1
        payload = b""
        background_tasks = BackgroundTasks()
        secret = "secret"

        lead = WebhookLead(
            lead_id=32294292,
            pipeline_id=3934218,
            new_status_id=55148413,
            custom_fields={
                596489: CustomFieldValue(name='Объект', value='1318551', enum=1318551),
                643043: CustomFieldValue(name='Дата окончания резерва', value='1687546800', enum=None),
            },
            tags={708334: 'Тестовая бронь'}
        )

        mock_compare_digest.return_value = True
        mock_user.return_value = user
        mock_import_meeting_service.return_value = "meeting"
        mock_get_lead_substage.return_value = "assign_agent"
        mock_parse_data.return_value = lead
        mock_get_booking_creation_status.return_value = True
        mock_booking_creation_from_amo_service.return_value = Booking(id="1111")
        mock_need_deactivate_bookings_task.return_value = False
        mock_is_different_amocrm_substage.return_value = False

        await _amocrm_webhook_view(payload, background_tasks, secret)

        mock_compare_digest.assert_called()
        mock_parse_data.assert_called()
        mock_user.assert_called()
        mock_import_meeting_service.assert_called()
        mock_get_lead_substage.assert_called()
        mock_booking_creation_from_amo_service.assert_called()
        mock_need_deactivate_bookings_task.assert_called()
        mock_is_different_amocrm_substage.assert_called()
        mock_update_booking_custom_fields.assert_called()
        mock_update_booking_status.assert_called()
        mock_update_booking_fixation_status.assert_called()
        mock_check_user_pinning_status.assert_called()
        mock_is_stage_valid.assert_called()
        mock_create_task_instance.assert_called()

        mock_booking_changes_logger.assert_not_called()
        mock_add_task.assert_not_called()
        mock_update_meeting_status.assert_not_called()

    @patch("src.booking.use_cases.amocrm_webhook.compare_digest")
    @patch("src.users.services.import_client_from_amo.ImportContactFromAmoService.__call__", new_callable=AsyncMock)
    @patch("src.meetings.services.import_meeting_from_amo.ImportMeetingFromAmoService.__call__",
           new_callable=AsyncMock)
    @patch("common.amocrm.amocrm.AmoCRM.get_lead_substage",)
    @patch("src.booking.use_cases.amocrm_webhook.AmoCRMWebhookCase._parse_data")
    @patch("src.booking.services.booking_creation.BookingCreationFromAmoService.__call__",
           new_callable=AsyncMock)
    @patch("src.booking.use_cases.amocrm_webhook.AmoCRMWebhookCase._update_booking_fixation_status",
           new_callable=AsyncMock)
    @patch("src.booking.use_cases.amocrm_webhook.AmoCRMWebhookCase._update_booking_status",
           new_callable=AsyncMock)
    @patch("src.booking.use_cases.amocrm_webhook.AmoCRMWebhookCase._update_booking_custom_fields",
           new_callable=AsyncMock)
    @patch("src.booking.use_cases.amocrm_webhook.AmoCRMWebhookCase._check_user_pinning_status",
           new_callable=AsyncMock)
    @patch("src.booking.loggers.wrappers.booking_changes_logger",  # booking_deactivate
           new_callable=AsyncMock)
    @patch("src.booking.use_cases.amocrm_webhook.AmoCRMWebhookCase._is_stage_valid",
           new_callable=AsyncMock)
    @patch("starlette.background.BackgroundTasks.add_task",
           new_callable=AsyncMock)
    @patch("src.booking.use_cases.amocrm_webhook.AmoCRMWebhookCase._update_meeting_status",
           new_callable=AsyncMock)
    @patch("src.booking.use_cases.amocrm_webhook.AmoCRMWebhookCase.create_task_instance",
           new_callable=AsyncMock)
    @patch("src.booking.use_cases.amocrm_webhook.AmoCRMWebhookCase._get_booking_creation_status",
           new_callable=AsyncMock)
    @patch("src.booking.use_cases.amocrm_webhook.AmoCRMWebhookCase._need_deactivate_bookings_task")
    @patch("src.booking.use_cases.amocrm_webhook.AmoCRMWebhookCase._is_different_amocrm_substage")
    @patch("src.booking.use_cases.amocrm_webhook.AmoCRMWebhookCase._get_booking", new_callable=AsyncMock)
    @patch("src.booking.use_cases.amocrm_webhook.AmoCRMWebhookCase._update_booking", new_callable=AsyncMock)
    async def test_booking_and_user_exist_and_no_new_status(
            self,
            mock_update_booking,
            mock_get_booking,
            mock_is_different_amocrm_substage,
            mock_need_deactivate_bookings_task,
            mock_get_booking_creation_status,
            mock_create_task_instance,
            mock_update_meeting_status,
            mock_add_task,
            mock_is_stage_valid,
            mock_booking_changes_logger,
            mock_check_user_pinning_status,
            mock_update_booking_custom_fields,
            mock_update_booking_status,
            mock_update_booking_fixation_status,
            mock_booking_creation_from_amo_service,
            mock_parse_data,
            mock_get_lead_substage,
            mock_import_meeting_service,
            mock_user,
            mock_compare_digest,
            user,
    ):
        # Case 2
        payload = b""
        background_tasks = BackgroundTasks()
        secret = "secret"

        lead = WebhookLead(
            lead_id=32294292,
            pipeline_id=3934218,
            new_status_id=55148413,
            custom_fields={
                596489: CustomFieldValue(name='Объект', value='1318551', enum=1318551),
                643043: CustomFieldValue(name='Дата окончания резерва', value='1687546800', enum=None),
            },
            tags={708334: 'Тестовая бронь'}
        )

        mock_compare_digest.return_value = True
        mock_user.return_value = user
        mock_import_meeting_service.return_value = "meeting"
        mock_get_lead_substage.return_value = "assign_agent"
        mock_parse_data.return_value = lead
        mock_get_booking_creation_status.return_value = True
        mock_get_booking.return_value = Booking(id="1111")
        mock_booking_creation_from_amo_service.return_value = Booking(id="1112")
        mock_need_deactivate_bookings_task.return_value = False
        mock_is_different_amocrm_substage.return_value = False
        mock_update_booking.return_value = Booking(id="1111")

        await _amocrm_webhook_view(payload, background_tasks, secret)

        mock_compare_digest.assert_called()
        mock_parse_data.assert_called()
        mock_user.assert_called()
        mock_import_meeting_service.assert_called()
        mock_get_lead_substage.assert_called()
        mock_need_deactivate_bookings_task.assert_called()
        mock_is_different_amocrm_substage.assert_called()
        mock_update_booking_custom_fields.assert_called()
        mock_update_booking_status.assert_called()
        mock_update_booking_fixation_status.assert_called()
        mock_check_user_pinning_status.assert_called()
        mock_is_stage_valid.assert_called()
        mock_create_task_instance.assert_called()

        mock_booking_creation_from_amo_service.assert_not_called()
        mock_booking_changes_logger.assert_not_called()
        mock_add_task.assert_not_called()
        mock_update_meeting_status.assert_not_called()

    @patch("src.booking.use_cases.amocrm_webhook.compare_digest")
    @patch("src.users.services.import_client_from_amo.ImportContactFromAmoService.__call__", new_callable=AsyncMock)
    @patch("src.meetings.services.import_meeting_from_amo.ImportMeetingFromAmoService.__call__",
           new_callable=AsyncMock)
    @patch("common.amocrm.amocrm.AmoCRM.get_lead_substage",)
    @patch("src.booking.use_cases.amocrm_webhook.AmoCRMWebhookCase._parse_data")
    @patch("src.booking.services.booking_creation.BookingCreationFromAmoService.__call__",
           new_callable=AsyncMock)
    @patch("src.booking.use_cases.amocrm_webhook.AmoCRMWebhookCase._update_booking_fixation_status",
           new_callable=AsyncMock)
    @patch("src.booking.use_cases.amocrm_webhook.AmoCRMWebhookCase._update_booking_status",
           new_callable=AsyncMock)
    @patch("src.booking.use_cases.amocrm_webhook.AmoCRMWebhookCase._update_booking_custom_fields",
           new_callable=AsyncMock)
    @patch("src.booking.use_cases.amocrm_webhook.AmoCRMWebhookCase._check_user_pinning_status",
           new_callable=AsyncMock)
    @patch("src.booking.loggers.wrappers.booking_changes_logger",  # booking_deactivate
           new_callable=AsyncMock)
    @patch("src.booking.use_cases.amocrm_webhook.AmoCRMWebhookCase._is_stage_valid",
           new_callable=AsyncMock)
    @patch("starlette.background.BackgroundTasks.add_task",
           new_callable=AsyncMock)
    @patch("src.booking.use_cases.amocrm_webhook.AmoCRMWebhookCase._update_meeting_status",
           new_callable=AsyncMock)
    @patch("src.booking.use_cases.amocrm_webhook.AmoCRMWebhookCase.create_task_instance",
           new_callable=AsyncMock)
    @patch("src.booking.use_cases.amocrm_webhook.AmoCRMWebhookCase._get_booking_creation_status",
           new_callable=AsyncMock)
    @patch("src.booking.use_cases.amocrm_webhook.AmoCRMWebhookCase._need_deactivate_bookings_task")
    @patch("src.booking.use_cases.amocrm_webhook.AmoCRMWebhookCase._is_different_amocrm_substage")
    @patch("src.booking.use_cases.amocrm_webhook.AmoCRMWebhookCase._get_booking", new_callable=AsyncMock)
    @patch("src.booking.use_cases.amocrm_webhook.AmoCRMWebhookCase._update_booking", new_callable=AsyncMock)
    async def test_receive_new_status(
            self,
            mock_update_booking,
            mock_get_booking,
            mock_is_different_amocrm_substage,
            mock_need_deactivate_bookings_task,
            mock_get_booking_creation_status,
            mock_create_task_instance,
            mock_update_meeting_status,
            mock_add_task,
            mock_is_stage_valid,
            mock_booking_changes_logger,
            mock_check_user_pinning_status,
            mock_update_booking_custom_fields,
            mock_update_booking_status,
            mock_update_booking_fixation_status,
            mock_booking_creation_from_amo_service,
            mock_parse_data,
            mock_get_lead_substage,
            mock_import_meeting_service,
            mock_user,
            mock_compare_digest,
            user,
    ):
        payload = b""
        background_tasks = BackgroundTasks()
        secret = "secret"

        lead = WebhookLead(
            lead_id=32294292,
            pipeline_id=3934218,
            new_status_id=55148413,
            custom_fields={
                596489: CustomFieldValue(name='Объект', value='1318551', enum=1318551),
                643043: CustomFieldValue(name='Дата окончания резерва', value='1687546800', enum=None),
            },
            tags={708334: 'Тестовая бронь'}
        )

        mock_compare_digest.return_value = True
        mock_user.return_value = user
        mock_import_meeting_service.return_value = "meeting"
        mock_get_lead_substage.return_value = "booking"
        mock_parse_data.return_value = lead
        mock_get_booking_creation_status.return_value = True
        mock_get_booking.return_value = Booking(id="1111")
        mock_booking_creation_from_amo_service.return_value = Booking(id="1112")
        mock_need_deactivate_bookings_task.return_value = False
        mock_is_different_amocrm_substage.return_value = True
        mock_update_booking.return_value = Booking(id="1111")

        await _amocrm_webhook_view(payload, background_tasks, secret)

        mock_compare_digest.assert_called()
        mock_parse_data.assert_called()
        mock_user.assert_called()
        mock_import_meeting_service.assert_called()
        mock_get_lead_substage.assert_called()
        mock_need_deactivate_bookings_task.assert_called()
        mock_is_different_amocrm_substage.assert_called()
        mock_update_booking_custom_fields.assert_called()
        mock_update_booking_status.assert_called()
        mock_update_booking_fixation_status.assert_called()
        mock_check_user_pinning_status.assert_called()
        mock_is_stage_valid.assert_called()
        mock_update_meeting_status.assert_called()

        mock_create_task_instance.assert_not_called()
        mock_booking_creation_from_amo_service.assert_not_called()
        mock_booking_changes_logger.assert_not_called()
        mock_add_task.assert_not_called()

    @patch("src.booking.use_cases.amocrm_webhook.compare_digest")
    @patch("src.booking.use_cases.amocrm_webhook.AmoCRMWebhookCase._parse_data")
    @patch("src.users.services.import_client_from_amo.ImportContactFromAmoService.__call__", new_callable=AsyncMock)
    @patch("src.task_management.services.update_task_status.UpdateTaskInstanceStatusService.__call__",
           new_callable=AsyncMock)
    @patch("src.booking.use_cases.amocrm_webhook.AmoCRMWebhookCase._update_booking_status", new_callable=AsyncMock)
    @patch("starlette.background.BackgroundTasks.add_task", new_callable=AsyncMock)
    @patch("src.task_management.services.create_task_instance.CreateTaskInstanceService.__call__",
           new_callable=AsyncMock)
    @patch("src.booking.use_cases.amocrm_webhook.AmoCRMWebhookCase._update_booking",
           new_callable=AsyncMock)
    async def test_update_booking_fixation_status(
            self,
            mock_update_booking,
            mock_create_task_instance_service,
            mock_add_task,
            mock_update_booking_status,
            mock_update_task_instance_service,
            mock_user,
            mock_parse_data,
            mock_compare_digest,
            user,
            amo_status_1305043,
            statuses_repo,
            booking_source_amocrm,
    ):
        payload = b""
        background_tasks = BackgroundTasks()
        secret = "secret"

        webhook_lead = WebhookLead(
            lead_id=32294292,
            pipeline_id=1305043,  # TYUMEN
            new_status_id=21197641,  # BOOKING
            custom_fields={
                643043: CustomFieldValue(name='Дата окончания резерва', value='1687546800', enum=None),
            },
        )

        mock_compare_digest.return_value = True
        mock_parse_data.return_value = webhook_lead
        mock_user.return_value = user

        await _amocrm_webhook_view(payload, background_tasks, secret)

        mock_compare_digest.assert_called()
        mock_update_task_instance_service.assert_called()
        mock_update_booking_status.assert_called()
        mock_create_task_instance_service.assert_called()
        mock_add_task.assert_called()
        mock_update_booking.assert_called()
