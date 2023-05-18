from pytz import UTC
from json import dumps
from pytest import mark
from datetime import datetime


@mark.asyncio
class TestAgentsShowtimesCreateView(object):
    async def test_success(self, client, agent, mocker, user_factory, agent_authorization):
        mocker.patch("src.showtimes.use_cases.AgentsShowtimesCreateCase._send_client_email")
        mocker.patch("src.showtimes.use_cases.AgentsShowtimesCreateCase._send_agent_email")
        mocker.patch("src.showtimes.use_cases.AgentsShowtimesCreateCase._send_strana_emails")
        user = await user_factory(agent_id=agent.id)
        payload = {"name": "test", "phone": user.phone, "visit": str(datetime.now(tz=UTC))}

        headers = {"Authorization": agent_authorization}

        response = await client.post("/showtimes/agents", headers=headers, data=dumps(payload))
        response_status = response.status_code

        awaitable_status = 204

        assert response_status == awaitable_status

    async def test_no_client(self, client, agent_authorization):
        payload = {"name": "test", "phone": "+78127234455", "visit": str(datetime.now(tz=UTC))}

        headers = {"Authorization": agent_authorization}

        response = await client.post("/showtimes/agents", headers=headers, data=dumps(payload))
        response_status = response.status_code
        response_json = response.json()
        response_reason = response_json["reason"]

        awaitable_status = 400
        awaitable_reason = "showtime_no_client"

        assert response_status == awaitable_status
        assert response_reason == awaitable_reason

    async def test_showtime_exists(self, client, agent, user_factory, agent_authorization):
        user = await user_factory(agent_id=agent.id)
        payload = {"name": "test", "phone": user.phone, "visit": str(datetime.now(tz=UTC))}

        headers = {"Authorization": agent_authorization}

        await client.post("/showtimes/agents", headers=headers, data=dumps(payload))
        response = await client.post("/showtimes/agents", headers=headers, data=dumps(payload))
        response_status = response.status_code
        awaitable_status = 204

        assert response_status == awaitable_status

    async def test_unauthorized(self, client):
        payload = {"name": "test", "phone": "+78127234455", "visit": str(datetime.now(tz=UTC))}

        response = await client.post("/showtimes/agents", data=dumps(payload))
        response_status = response.status_code

        awaitable_status = 401

        assert response_status == awaitable_status

    async def test_success_with_project(
        self, client, agent, mocker, user_factory, agent_authorization, project_factory
    ):
        project = await project_factory(i=0)
        mocker.patch("src.showtimes.use_cases.AgentsShowtimesCreateCase._send_client_email")
        mocker.patch("src.showtimes.use_cases.AgentsShowtimesCreateCase._send_agent_email")
        mocker.patch("src.showtimes.use_cases.AgentsShowtimesCreateCase._send_strana_emails")
        settings_mock = mocker.patch("src.showtimes.api.showtime.amocrm.AmoCRM._fetch_settings")
        create_showtime_mock = mocker.patch("src.showtimes.api.showtime.amocrm.AmoCRM.create_showtime")
        update_showtime_mock = mocker.patch("src.showtimes.api.showtime.amocrm.AmoCRM.update_showtime")
        create_showtime_mock.return_value = [
            {
                'id': 100,
            }
        ]
        user = await user_factory(agent_id=agent.id)
        payload = {"name": "test", "phone": user.phone, "visit": str(datetime.now(tz=UTC)), 'project_id': project.id}

        headers = {"Authorization": agent_authorization}

        response = await client.post("/showtimes/agents", headers=headers, data=dumps(payload))
        response_status = response.status_code

        awaitable_status = 204

        assert response_status == awaitable_status

        update_showtime_mock.assert_called_once()
