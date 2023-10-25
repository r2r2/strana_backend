import pytest


pytestmark = pytest.mark.asyncio


class TestSetPreviousTaskStatusCase:

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
        task_instance_repo,
        task_status,
        task_status_2,
        task_instance,
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
        assert task.status.slug == task_status.slug