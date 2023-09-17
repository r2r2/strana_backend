import pytest


pytestmark = pytest.mark.asyncio


class TestSetPreviousTaskStatusCase:
    @pytest.fixture
    async def setup(self, task_chain_repo, task_status_repo, task_instance_repo, booking):
        task_chain = await task_chain_repo.create(data=dict(name="test_name"))
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
        task_instance = await task_instance_repo.create(
            data=dict(
                status=task_status_2,
                booking=booking,
            )
        )
        return task_instance, task_status_1, task_status_2

    @pytest.mark.parametrize(
        "task_id, status_code, should_raise_error",
        [
            (1, 200, False),
            (22, 404, True),
            ("task_id", 422, True),
        ]
    )
    async def test_set_previous_status(
        self,
        agent_authorization,
        async_client,
        task_id,
        status_code,
        should_raise_error,
        setup,
        task_instance_repo,
    ):
        headers = {"Authorization": agent_authorization}
        response = await async_client.post(
            f"task_management/tasks/{task_id}/previous_status",
            headers=headers,
        )

        assert response.status_code == status_code

        if should_raise_error:
            return

        task = await task_instance_repo.retrieve(
            filters=dict(id=task_id),
            related_fields=["status"],
        )
        assert task.status.slug == setup[1].slug
