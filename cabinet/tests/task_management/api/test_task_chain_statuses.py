import pytest

from tests.task_management.api.test_cases.task_chain_statuses import TaskChainStatusesCaseTestData


pytestmark = pytest.mark.asyncio


class TestTaskChainStatusesCase:
    @pytest.fixture
    async def task_chain_and_statuses(self, task_chain_repo, task_status_repo):
        task_chain = await task_chain_repo.create(data=dict(name="test_name", sensei_pid=999))
        task_status_1 = await task_status_repo.create(
            data=dict(
                name="test_name_1",
                slug="test_slug_1",
                description="test_description_1",
                type="test_type_1",
                priority=1,
                tasks_chain=task_chain,
            )
        )
        task_status_2 = await task_status_repo.create(
            data=dict(
                name="test_name_2",
                slug="test_slug_2",
                description="test_description_2",
                type="test_type_2",
                priority=2,
                tasks_chain=task_chain,
            )
        )
        return task_chain, task_status_1, task_status_2

    @pytest.mark.parametrize(
        "slug, expected, status_code",
        TaskChainStatusesCaseTestData().get_statuses_case()
    )
    async def test_get_statuses(
        self,
        agent_authorization,
        async_client,
        slug,
        expected,
        status_code,
        task_chain_and_statuses,
    ):
        headers = {"Authorization": agent_authorization}
        response = await async_client.get(
            f"task_management/task_chain/statuses?slug={slug}",
            headers=headers,
        )

        assert response.status_code == status_code
        assert response.json() == expected
