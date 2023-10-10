import uuid
from unittest.mock import patch

import pytest
from fastapi import status
from mock.mock import AsyncMock

pytestmark = pytest.mark.asyncio


class TestSberbankStatusApi:

    @pytest.mark.parametrize("kind", ["wrong_value"])
    async def test_sberbank_status_view_422(
            self,
            async_client,
            kind,
    ):
        payment_id = 123456
        secret = "test_secret"
        response = await async_client.get(
            f"/booking/sberbank/{secret}/{kind}?orderId={payment_id}"
        )

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    @pytest.mark.parametrize("kind", ["success", "fail"])
    async def test_sberbank_status_view_404(
            self,
            async_client,
            kind,
    ):
        payment_id = str(uuid.uuid4())
        secret = "test_secret"
        response = await async_client.get(
            f"/booking/sberbank/{secret}/{kind}?orderId={payment_id}"
        )

        assert response.status_code == status.HTTP_404_NOT_FOUND

    @pytest.mark.parametrize("kind", ["success", "fail"])
    async def test_sberbank_status_view_400(
            self,
            async_client,
            booking,
            booking_repo,
            kind,
    ):
        secret = "test_secret"
        test_booking = await booking_repo.update(await booking, dict(payment_id=str(uuid.uuid4())))
        response = await async_client.get(
            f"/booking/sberbank/{secret}/{kind}?orderId={test_booking.payment_id}"
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    @pytest.mark.skip(reason="need to fix")
    @pytest.mark.parametrize("kind", ["success", "fail"])
    async def test_sberbank_status_view__payment_not_succeed(
            self,
            async_client,
            booking,
            booking_repo,
            kind,
            mocker,
            monkeypatch,
    ):
        secret = "test_secret"
        with patch('src.booking.use_cases.sberbank_status.compare_digest') as mock_compare_digest, \
                patch('src.booking.use_cases.SberbankStatusCase._check_status', new_callable=AsyncMock) as mock__check_status:
            mock_compare_digest.return_value = True
            mock__check_status.return_value = {"orderStatus": 3}

            test_booking = await booking_repo.update(await booking, dict(payment_id=str(uuid.uuid4())))
            response = await async_client.get(
                f"/booking/sberbank/{secret}/{kind}?orderId={test_booking.payment_id}"
            )

            assert response.status_code == status.HTTP_307_TEMPORARY_REDIRECT
            assert response.headers["Location"] == f"None/booking/{test_booking.id}/4/?status={kind}"
