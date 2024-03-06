import pytest
from unittest.mock import patch, AsyncMock

from src.users.api.amocrm.amocrm_webhook import _amocrm_contact_webhook
from src.booking.types import CustomFieldValue, WebhookContact

pytestmark = pytest.mark.asyncio


class TestContactWebhook:
    secret = "secret"

    @patch("src.users.use_cases.amocrm_contact_webhook")
    async def test_amocrm_contact_webhook(
            self,
            mock_compare_digest
    ):
        payload = b""
        secret = "secret"

        mock_compare_digest.return_value = True

        await _amocrm_contact_webhook(payload, secret)

    @patch("src.users.use_cases.amocrm_contact_webhook.compare_digest")
    @patch(
        "src.users.services.import_contact_from_amo.ImportContactFromAmoService.__call__",
        new_callable=AsyncMock
    )
    async def test_contact_webhook_without_custom_fields(
            self,
            mock_user,
            mock_compare_digest,
            user
    ):
        payload = b""
        secret = "secret"

        mock_compare_digest.return_value = True
        mock_user.return_value = user

        await _amocrm_contact_webhook(payload, secret)

        mock_compare_digest.assert_called()
        mock_user.assert_called()

    @patch("src.users.use_cases.amocrm_contact_webhook.compare_digest")
    @patch(
        "src.users.services.import_contact_from_amo.ImportContactFromAmoService.__call__",
        new_callable=AsyncMock
    )
    @patch("src.users.use_cases.amocrm_contact_webhook.AmoCRMContactWebhookCase._parse_contact_data")
    async def test_contact_webhook_with_custom_fields(
            self,
            mock_parse_contact_data,
            mock_user,
            mock_compare_digest,
            user
    ):
        payload = b""
        secret = "secret"

        contact = WebhookContact(
            amocrm_id=123123123,
            fullname="Тестовичков Тест Тестович",
            custom_fields={
                362093: CustomFieldValue(name='Телефон', value=' 79965713734', enum=706657),
                362095: CustomFieldValue(name='Email', value='zema8382@gmai.com', enum=706665),
            },
            tags={
                555355: "клиент"
            },
            role=555355,
        )

        mock_compare_digest.return_value = True
        mock_user.return_value = user
        mock_parse_contact_data.return_value = contact

        await _amocrm_contact_webhook(payload, secret)
        mock_compare_digest.assert_called()
        mock_parse_contact_data.assert_called()
        mock_user.assert_called()
