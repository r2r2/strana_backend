from http import HTTPStatus

import pytest
from mock import patch, AsyncMock


pytestmark = pytest.mark.asyncio


class TestGetMortgageTextBlock:

    @pytest.mark.parametrize(
        "city_slug, found",
        [
            ("msk", True),
            ("do_not_exists", False),
        ],
    )
    async def test_get_mortgage_text_block(
        self,
        async_client,
        user_authorization,
        city_slug,
        found,
        mortgage_text_block,
    ):
        mock_send_sentry_log: str = "src.mortgage.use_cases.text_block.GetMortgageTextBlockCase._send_sentry_log"
        headers = {"Authorization": user_authorization}
        with patch(mock_send_sentry_log, new_callable=AsyncMock):
            response = await async_client.get(
                f"mortgage/text_blocks/{city_slug}",
                headers=headers,
            )

        assert response.status_code == HTTPStatus.OK
        if found:
            assert response.json() is not None
        else:
            assert response.json() is None
