from http import HTTPStatus

import pytest


pytestmark = pytest.mark.asyncio


class TestGetTaskInstanceCase:
    async def test_get_task_instance(
        self,
        async_client,
        user_authorization,
        task_instance,
    ):
        headers = {"Authorization": user_authorization}
        response = await async_client.get(
            f"/task_management/task_instance/{task_instance.id}",
            headers=headers,
        )

        assert response.status_code == HTTPStatus.OK
