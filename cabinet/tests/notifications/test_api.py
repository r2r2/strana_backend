from http import HTTPStatus

import pytest

from src.users.constants import UserAssignSlug


pytestmark = pytest.mark.asyncio


@pytest.mark.parametrize("slug", [slug.value for slug in UserAssignSlug])
async def test_client_assign_templates_text(
    async_client,
    slug,
    user_token_query,
    user,
    agent_1,
    user_repo,
    assign_client_template,
):
    await user_repo.update(user, data=dict(agent_id=agent_1.id))
    response = await async_client.get(f"templates/assign/{slug}?{user_token_query}")
    assert response.status_code == HTTPStatus.OK
    await user_repo.delete(user)
    await user_repo.delete(agent_1)


async def test_sms_help_text(
    async_client,
    user_authorization,
    assign_client_template,
):
    headers = {"Authorization": user_authorization}
    response = await async_client.get(f"templates/assign/sms_text?project_id=1", headers=headers)
    assert response.status_code == HTTPStatus.OK
