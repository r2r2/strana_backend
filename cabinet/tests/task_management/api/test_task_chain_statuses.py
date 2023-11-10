import pytest

from tests.task_management.api.test_cases.task_chain_statuses import TaskChainStatusesCaseTestData


pytestmark = pytest.mark.asyncio


class TestTaskChainStatusesCase:

    @pytest.mark.parametrize(
        "expected, status_code",
        TaskChainStatusesCaseTestData().get_statuses_case()
    )
    async def test_get_statuses(
        self,
        agent_authorization,
        async_client,
        expected,
        status_code,
        task_status,
        task_status_2,
        task_chain,
        task_group_status,
        task_instance,
    ):
        headers = {"Authorization": agent_authorization}
        response = await async_client.get(
            f"task_management/task_chain/statuses?taskId={task_instance.id}",
            headers=headers,
        )
        assert response.status_code == status_code
        assert response.json() == expected
