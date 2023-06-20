from http import HTTPStatus

import pytest


pytestmark = pytest.mark.asyncio


class TestAgreementGetDocument:
    @pytest.mark.parametrize("agreement_id", [1])
    async def test_agent_get_document(
        self,
        agreement_id,
        async_client,
        agent_authorization,
        agreement,
    ):

        headers = {"Authorization": agent_authorization}
        response = await async_client.get(
            f"agencies/agent/agreements/{agreement_id}/get_document",
            headers=headers,
        )
        assert response.status_code == HTTPStatus.OK

    @pytest.mark.parametrize("agreement_id", [1])
    async def test_admin_get_document(
        self,
        agreement_id,
        async_client,
        admin_authorization,
        agreement,
    ):

        headers = {"Authorization": admin_authorization}
        response = await async_client.get(
            f"agencies/admin/agreements/{agreement_id}/get_document",
            headers=headers,
        )
        assert response.status_code == HTTPStatus.OK

    # @pytest.mark.parametrize("agreement_id", [1])
    # async def test_repres_get_document(
    #     self,
    #     agreement_id,
    #     async_client,
    #     repres_authorization,
    #     agreement,
    # ):
    #     # todo: need to fix: tortoise.exceptions.IntegrityError: UNIQUE constraint failed: users_user.maintained_id
    #     headers = {"Authorization": repres_authorization}
    #     response = await async_client.get(
    #         f"agencies/repres/agreements/{agreement_id}/get_document",
    #         headers=headers,
    #     )
    #     assert response.status_code == HTTPStatus.OK
