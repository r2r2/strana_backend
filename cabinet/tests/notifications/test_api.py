from http import HTTPStatus

import pytest
from httpx import Response

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


@pytest.mark.parametrize("slug", ["wrong_slug"])
async def test_wrong_templates_text(
    async_client,
    slug,
):
    response = await async_client.get(f"templates/{slug}")
    assert response.status_code == HTTPStatus.BAD_REQUEST


@pytest.mark.parametrize("slug", ["main_page_slug"])
async def test_get_templates_text(
    async_client,
    main_page_repo,
    slug,
):
    main_page_text_data: dict = dict(
        title="main_page_title",
        slug=slug,
        text="main_page_text",
    )
    await main_page_repo.create(data=main_page_text_data)
    response: Response = await async_client.get(f"templates/{slug}")
    main_page_text_response = dict(title="main_page_title", text="main_page_text")

    assert response.status_code == HTTPStatus.OK
    assert response.json() == main_page_text_response


# async def test_sms_help_text(
#     async_client,
#     user_authorization,
#     assign_client_template,
# ):
#     headers = {"Authorization": user_authorization}
#     response = await async_client.get(
#     f"templates/assign/sms_text?project_id=1", headers=headers)
#     assert response.status_code == HTTPStatus.OK
