import pytest

from unittest.mock import patch, AsyncMock

from common import security

# All test coroutines will be treated as marked.
pytestmark = pytest.mark.asyncio


class TestAgentChangePasswordCase:
    async def test_user_change_password_403(self, async_client, user_authorization):
        headers = {"Authorization": user_authorization}
        response = await async_client.patch("/agents/change_password", headers=headers)
        assert response.status_code == 403

    async def test_agent_change_different_password_422(
        self,
        async_client,
        agent_authorization,
        faker,
    ):
        headers = {"Authorization": agent_authorization}
        payload = dict(
            password_1=faker.password(),
            password_2=faker.password(),
        )
        response = await async_client.patch("/agents/change_password", headers=headers, json=payload)

        # общий ответ апи
        assert response.status_code == 422
        assert response.json()["detail"][0]["msg"] == "passwords_not_match"

    async def test_agent_change_short_password_422(
        self,
        async_client,
        agent_authorization,
        faker,
    ):
        password = faker.password()[:6]
        headers = {"Authorization": agent_authorization}
        payload = dict(
            password_1=password,
            password_2=password,
        )
        response = await async_client.patch("/agents/change_password", headers=headers, json=payload)

        # общий ответ апи
        assert response.status_code == 422
        assert response.json()["detail"][0]["msg"] == "passwords_too_short"

    @patch("starlette.requests.HTTPConnection.session")
    async def test_agent_change_is_not_approved_400(
        self,
        mock_requests_session,
        async_client,
        agent_not_approved_authorization,
        faker,
    ):
        password = faker.password()
        headers = {"Authorization": agent_not_approved_authorization}
        payload = dict(
            password_1=password,
            password_2=password,
        )
        response = await async_client.patch("/agents/change_password", headers=headers, json=payload)

        # общий ответ апи
        assert response.status_code == 400
        assert response.json()["reason"] == "user_change_password"

    @patch("starlette.requests.HTTPConnection.session")
    async def test_agent_change_same_password_400(
        self,
        mock_requests_session,
        async_client,
        agent_authorization,
    ):
        headers = {"Authorization": agent_authorization}
        payload = dict(
            password_1="12345678",
            password_2="12345678",
        )
        response = await async_client.patch("/agents/change_password", headers=headers, json=payload)

        # общий ответ апи
        assert response.status_code == 400
        assert response.json()["reason"] == "user_same_password"


    @patch("starlette.requests.HTTPConnection.session", new_callable=AsyncMock)
    async def test_agent_change_password(
        self,
        mock_requests_session,
        async_client,
        agent,
        agent_authorization,
        user_repo,
        faker,
    ):
        password = faker.password()
        headers = {"Authorization": agent_authorization}
        payload = dict(
            password_1=password,
            password_2=password,
        )
        response = await async_client.patch("/agents/change_password", headers=headers, json=payload)

        # получаем данные из тестовой БД для проверки
        updated_agent = await user_repo.retrieve(filters=dict(id=agent.id))

        # общий ответ апи
        assert response.status_code == 200
        assert response.json()["id"] == agent.id

        # проверяем, что пароль изменился
        assert updated_agent.password != security.get_hasher().hash(password)
