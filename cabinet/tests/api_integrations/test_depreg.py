import unittest
from typing import Any
from unittest.mock import patch
from common.depreg import DepregAPI
from common.depreg.dto.depreg_response import DepregParticipantsDTO


class TestDepregAPI(unittest.IsolatedAsyncioTestCase):
    config = {
        "base_url": "https://api.example.com",
        "auth_type": "Bearer",
        "token": "test-token",
    }

    @patch("common.depreg.depreg_api.DepregAPI._make_request")
    @patch("common.depreg.depreg_api.DepregAPI._get_session")
    async def test_get_participants_success(
        self,
        mock_client_session,
        mock_make_request,
    ):
        test_data: list[dict[str, Any]] = [{"id": 1, "eventId": 123}]
        mock_make_request.return_value.data = test_data
        api = DepregAPI(self.config)
        async with api:
            participants = await api.get_participants(123)
        expected_result = DepregParticipantsDTO(**{"data": test_data})
        self.assertEqual(participants, expected_result)
