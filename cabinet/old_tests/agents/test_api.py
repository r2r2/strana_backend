from json import dumps

import httpx
from json import dumps, loads
from pytest import mark
from secrets import token_urlsafe

from src.booking.constants import BookingSubstages
from src.booking.repos import Booking
from functools import partial


@mark.asyncio
class TestProcessRegisterView(object):
    async def test_success(self, client, agency, mocker, agent_repo, agency_repo):
        mocker.patch("src.agents.use_cases.ProcessRegisterCase._send_confirm_email")
        mocker.patch("src.agents.use_cases.ProcessRegisterCase._send_agency_email")
        mocker.patch("src.agents.use_cases.ProcessRegisterCase._import_contacts")
        await agency_repo.update(agency, {"is_approved": True})

        payload = {
            "name": "test",
            "surname": "test",
            "patronymic": "test",
            "phone": "+78005553535",
            "password_1": "testtest",
            "password_2": "testtest",
            "email": "test@gmail.com",
            "agency": agency.id,
            "is_contracted": True,
        }

        response = await client.post("/agents/register", data=dumps(payload))
        response_status = response.status_code

        agent = await agent_repo.retrieve({"phone": "+78005553535"})

        awaitable_status = 201
        awaitable_type = "agent"

        assert agent.duty_type is None
        assert agent.is_active is False
        assert agent.is_approved is True
        assert agent.password is not None
        assert agent.type == awaitable_type
        assert agent.email_token is not None
        assert response_status == awaitable_status

    async def test_no_agency(self, client, agency, agent_repo):
        payload = {
            "name": "test",
            "surname": "test",
            "patronymic": "test",
            "phone": "+78005553535",
            "password_1": "testtest",
            "password_2": "testtest",
            "email": "test@gmail.com",
            "agency": agency.id,
            "is_contracted": True,
        }

        response = await client.post("/agents/register", data=dumps(payload))
        response_status = response.status_code
        response_json = response.json()
        response_reason = response_json["reason"]

        agent = await agent_repo.retrieve({"phone": "+78005553535"})

        awaitable_status = 400
        awaitable_reason = "agent_no_agency"

        assert agent is None
        assert response_status == awaitable_status
        assert response_reason == awaitable_reason

    async def test_email_taken(
        self,
        client,
        agent,
        agency,
        admin_repo,
        agency_repo,
        agent_repo,
        repres_repo,
        user_repo,
        admin_factory,
        repres_factory,
        user_factory,
    ):
        admin = await admin_factory(email="test@gmail.com")
        repres = await repres_factory(email="test@gmail.com")
        user = await user_factory(email="test@gmail.com")
        await admin_repo.update(admin, {"is_active": True})
        await repres_repo.update(repres, {"is_active": True})
        await user_repo.update(user, {"is_active": True})

        await agency_repo.update(agency, {"is_approved": True})
        await agent_repo.update(agent, {"email": "test@gmail.com", "is_active": True})
        payload = {
            "name": "test",
            "surname": "test",
            "patronymic": "test",
            "phone": "+78005553535",
            "password_1": "testtest",
            "password_2": "testtest",
            "email": "Test@gmail.com",
            "agency": agency.id,
            "is_contracted": True,
        }

        response = await client.post("/agents/register", data=dumps(payload))
        response_status = response.status_code
        response_json = response.json()
        response_reason = response_json["reason"]

        agent = await agent_repo.retrieve({"phone": "+78005553535"})

        awaitable_status = 400
        awaitable_reason = "agent_already_registered"

        assert agent is None
        assert response_status == awaitable_status
        assert response_reason == awaitable_reason

    async def test_already_registered(
        self,
        client,
        agent,
        agency,
        agency_repo,
        admin_factory,
        repres_factory,
        user_factory,
        admin_repo,
        repres_repo,
        user_repo,
    ):
        admin = await admin_factory(email=agent.email)
        repres = await repres_factory(email=agent.email)
        user = await user_factory(email=agent.email)
        await admin_repo.update(admin, {"is_active": True})
        await repres_repo.update(repres, {"is_active": True})
        await user_repo.update(user, {"is_active": True})

        await agency_repo.update(agency, {"is_approved": True})
        payload = {
            "name": agent.name,
            "surname": agent.surname,
            "patronymic": agent.patronymic,
            "phone": agent.phone,
            "password_1": "testtest",
            "password_2": "testtest",
            "email": agent.email.upper(),
            "agency": agency.id,
            "is_contracted": True,
        }

        response = await client.post("/agents/register", data=dumps(payload))
        response_status = response.status_code
        response_json = response.json()
        response_reason = response_json["reason"]

        awaitable_status = 400
        awaitable_reason = "agent_already_registered"

        assert response_status == awaitable_status
        assert response_reason == awaitable_reason

    async def test_deleted_is_overridden(
        self,
        client,
        mocker,
        agent,
        agency,
        agency_repo,
        admin_factory,
        repres_factory,
        user_factory,
        admin_repo,
        repres_repo,
        agent_repo,
        user_repo,
    ):
        """Удалённый агент удаляется из бд и создаётся новый."""
        mocker.patch('src.agents.use_cases.process_register.ProcessRegisterCase._import_contacts')
        mocker.patch('src.agents.use_cases.process_register.ProcessRegisterCase._send_confirm_email')
        mocker.patch('src.agents.use_cases.process_register.ProcessRegisterCase._send_agency_email')

        admin = await admin_factory(email=agent.email)
        repres = await repres_factory(email=agent.email)
        user = await user_factory(email=agent.email)
        await admin_repo.update(admin, {"is_active": True})
        await repres_repo.update(repres, {"is_active": True})
        await user_repo.update(user, {"is_active": True})

        await agency_repo.update(agency, {"is_approved": True})
        await agent_repo.update(agent, {"is_deleted": True})
        payload = {
            "name": agent.name,
            "surname": agent.surname,
            "patronymic": agent.patronymic,
            "phone": agent.phone,
            "password_1": "testtest",
            "password_2": "testtest",
            "email": agent.email.upper(),
            "agency": agency.id,
            "is_contracted": True,
        }

        response = await client.post("/agents/register", data=dumps(payload))
        response_status = response.status_code

        awaitable_status = 201

        assert response_status == awaitable_status

    async def test_not_approved(
        self,
        client,
        agent,
        agency,
        agency_repo,
        agent_repo,
        admin_factory,
        repres_factory,
        user_factory,
        admin_repo,
        repres_repo,
        user_repo,
    ):
        admin = await admin_factory(email=agent.email)
        repres = await repres_factory(email=agent.email)
        user = await user_factory(email=agent.email)
        await admin_repo.update(admin, {"is_active": True})
        await repres_repo.update(repres, {"is_active": True})
        await user_repo.update(user, {"is_active": True})

        await agent_repo.update(agent, {"is_approved": False})
        await agency_repo.update(agency, {"is_approved": True})
        payload = {
            "name": agent.name,
            "surname": agent.surname,
            "patronymic": agent.patronymic,
            "phone": agent.phone,
            "password_1": "testtest",
            "password_2": "testtest",
            "email": agent.email.upper(),
            "agency": agency.id,
            "is_contracted": True,
        }

        response = await client.post("/agents/register", data=dumps(payload))
        response_status = response.status_code
        response_json = response.json()
        response_reason = response_json["reason"]

        awaitable_status = 400
        awaitable_reason = "agent_not_approved"

        assert response_status == awaitable_status
        assert response_reason == awaitable_reason

    async def test_password_too_short(self, client, agency, mocker, agent_repo, agency_repo):
        mocker.patch("src.agents.use_cases.ProcessRegisterCase._send_confirm_email")
        mocker.patch("src.agents.use_cases.ProcessRegisterCase._send_agency_email")
        mocker.patch("src.agents.use_cases.ProcessRegisterCase._import_contacts")
        await agency_repo.update(agency, {"is_approved": True})

        payload = {
            "name": "test",
            "surname": "test",
            "patronymic": "test",
            "phone": "+78005553535",
            "password_1": "test",
            "password_2": "test",
            "email": "test@gmail.com",
            "agency": agency.id,
            "is_contracted": True,
        }

        response = await client.post("/agents/register", data=dumps(payload))
        response_status = response.status_code
        awaitable_status = 422

        assert response_status == awaitable_status

    async def test_password_doesnt_match(self, client, agency, mocker, agent_repo, agency_repo):
        mocker.patch("src.agents.use_cases.ProcessRegisterCase._send_confirm_email")
        mocker.patch("src.agents.use_cases.ProcessRegisterCase._send_agency_email")
        mocker.patch("src.agents.use_cases.ProcessRegisterCase._import_contacts")
        await agency_repo.update(agency, {"is_approved": True})

        payload = {
            "name": "test",
            "surname": "test",
            "patronymic": "test",
            "phone": "+78005553535",
            "password_1": "testtest",
            "password_2": "testtest1",
            "email": "test@gmail.com",
            "agency": agency.id,
            "is_contracted": True,
        }

        response = await client.post("/agents/register", data=dumps(payload))
        response_status = response.status_code
        response_json = response.json()
        response_reason = response_json["reason"]

        awaitable_status = 400
        awaitable_reason = "agent_passwords_doesnt_match"

        assert response_status == awaitable_status
        assert response_reason == awaitable_reason


@mark.asyncio
class TestConfirmEmailView(object):
    async def test_success(self, client, agent, agent_repo, create_email_token, repres):
        await agent_repo.update(agent, {"is_active": False})
        token = create_email_token(agent.id)

        await client.get(f"/agents/confirm_email?q={token}&p={agent.email_token}")

        agent = await agent_repo.retrieve({"id": agent.id})

        assert agent.is_active is True
        assert agent.email_token is None

    async def test_fail(self, client, agent, agent_repo, create_email_token):
        await agent_repo.update(agent, {"is_active": False})
        token = create_email_token(agent.id)

        await client.get(f"/agents/confirm_email?q={token}&p={agent.email_token}12")

        agent = await agent_repo.retrieve({"id": agent.id})

        assert agent.is_active is False
        assert agent.email_token is not None

    async def test_already_active(self, client, agent, agent_repo, create_email_token):
        token = create_email_token(agent.id)

        await client.get(f"/agents/confirm_email?q={token}&p={agent.email_token}")

        agent = await agent_repo.retrieve({"id": agent.id})

        assert agent.is_active is True
        assert agent.email_token is not None


@mark.asyncio
class TestEmailResetView(object):
    async def test_success(self, client, agent, mocker, agent_repo):
        mocker.patch("src.agents.use_cases.EmailResetCase._send_email")
        payload = {"email": agent.email.upper()}

        response = await client.post("/agents/email_reset", data=dumps(payload))
        response_status = response.status_code

        agent = await agent_repo.retrieve({"id": agent.id})

        awaitable_status = 204

        assert agent.discard_token is not None
        assert response_status == awaitable_status

    async def test_not_found(self, client, agent, agent_repo):
        await agent_repo.update(agent, {"is_active": False})
        payload = {"email": agent.email}

        response = await client.post("/agents/email_reset", data=dumps(payload))
        response_status = response.status_code
        response_json = response.json()
        response_reason = response_json["reason"]

        agent = await agent_repo.retrieve({"id": agent.id})

        awaitable_status = 404
        awaitable_reason = "agent_not_found"

        assert agent.discard_token is None
        assert response_status == awaitable_status
        assert response_reason == awaitable_reason

    async def test_not_approved(self, client, agent, agent_repo):
        await agent_repo.update(agent, {"is_approved": False})
        payload = {"email": agent.email}

        response = await client.post("/agents/email_reset", data=dumps(payload))
        response_status = response.status_code
        response_json = response.json()
        response_reason = response_json["reason"]

        agent = await agent_repo.retrieve({"id": agent.id})

        awaitable_status = 400
        awaitable_reason = "agent_not_approved"

        assert agent.discard_token is None
        assert response_status == awaitable_status
        assert response_reason == awaitable_reason


@mark.asyncio
class TestResetPasswordView(object):
    async def test_success(self, client, agent, mocker, agent_repo, create_email_token):
        mocker.patch("src.agents.use_cases.ResetPasswordCase._remove_discard")
        await agent_repo.update(agent, {"discard_token": token_urlsafe(32)})

        token = create_email_token(agent.id)

        await client.get(f"/agents/reset_password?q={token}&p={agent.discard_token}")

        agent = await agent_repo.retrieve({"id": agent.id})

        assert agent.discard_token is None
        assert agent.reset_time is not None

    async def test_fail(self, client, agent, agent_repo, create_email_token):
        await agent_repo.update(agent, {"discard_token": token_urlsafe(32), "is_active": False})

        token = create_email_token(agent.id)

        await client.get(f"/agents/reset_password?q={token}&p={agent.discard_token}fsdfsd")

        agent = await agent_repo.retrieve({"id": agent.id})

        assert agent.reset_time is None
        assert agent.discard_token is not None


@mark.asyncio
class TestChangePasswordView(object):
    async def test_success(self, client, agent_authorization):
        payload = {"password_1": "testtest", "password_2": "testtest"}
        headers = {"Authorization": agent_authorization}

        response = await client.patch(
            "/agents/change_password", data=dumps(payload), headers=headers
        )
        response_status = response.status_code

        awaitable_status = 204

        assert response_status == awaitable_status

    async def test_no_agent_id(self, client):
        payload = {"password_1": "testtest", "password_2": "testtest"}

        response = await client.patch("/agents/change_password", data=dumps(payload))
        response_status = response.status_code
        response_json = response.json()
        response_reason = response_json["reason"]

        awaitable_status = 400
        awaitable_reason = "agent_change_password"

        assert response_status == awaitable_status
        assert response_reason == awaitable_reason

    async def test_no_agent(self, client, agent, agent_repo, agent_authorization):
        await agent_repo.update(agent, {"is_active": False})
        payload = {"password_1": "testtest", "password_2": "testtest"}
        headers = {"Authorization": agent_authorization}

        response = await client.patch(
            "/agents/change_password", data=dumps(payload), headers=headers
        )
        response_status = response.status_code
        response_json = response.json()
        response_reason = response_json["reason"]

        awaitable_status = 400
        awaitable_reason = "agent_change_password"

        assert response_status == awaitable_status
        assert response_reason == awaitable_reason


@mark.asyncio
class TestProcessLoginView(object):
    async def _register(self, client, mocker, agency, agent_repo, agency_repo):
        mocker.patch("src.agents.use_cases.ProcessRegisterCase._send_confirm_email")
        mocker.patch("src.agents.use_cases.ProcessRegisterCase._send_agency_email")
        mocker.patch("src.agents.use_cases.ProcessRegisterCase._import_contacts")
        await agency_repo.update(agency, {"is_approved": True})
        payload = {
            "name": "test",
            "surname": "test",
            "patronymic": "test",
            "phone": "+78005553535",
            "password_1": "testtest",
            "password_2": "testtest",
            "email": "test@gmail.com",
            "agency": agency.id,
            "is_contracted": True,
        }
        response = await client.post("/agents/register", data=dumps(payload))
        response_json = response.json()
        response_id = response_json["id"]

        agent = await agent_repo.retrieve({"id": response_id})
        agent = await agent_repo.update(agent, {"is_active": True, "is_approved": True})

        return agent

    async def test_success(self, client, mocker, agency, agent_repo, agency_repo):
        agent = await self._register(client, mocker, agency, agent_repo, agency_repo)
        mocker.patch("src.agents.use_cases.ProcessLoginCase._remove_change_password_permission")

        payload = {"email": agent.email.upper(), "password": "testtest"}

        response = await client.post("/agents/login", data=dumps(payload))
        response_status = response.status_code

        awaitable_status = 200

        assert response_status == awaitable_status

    async def test_fail(self, client, mocker, agency, agent_repo, agency_repo):
        agent = await self._register(client, mocker, agency, agent_repo, agency_repo)

        payload = {"email": agent.email.upper(), "password": "testtest1"}

        response = await client.post("/agents/login", data=dumps(payload))
        response_status = response.status_code
        response_json = response.json()
        response_reason = response_json["reason"]

        awaitable_status = 400
        awaitable_reason = "agent_password_wrong"

        assert response_status == awaitable_status
        assert response_reason == awaitable_reason

    async def test_not_found(self, client):
        payload = {"email": "wrong@gmail.com", "password": "testtest1"}

        response = await client.post("/agents/login", data=dumps(payload))
        response_status = response.status_code
        response_json = response.json()
        response_reason = response_json["reason"]

        awaitable_status = 404
        awaitable_reason = "agent_not_found"

        assert response_status == awaitable_status
        assert response_reason == awaitable_reason

    async def test_not_approved(self, client, mocker, agency, agent_repo, agency_repo):
        agent = await self._register(client, mocker, agency, agent_repo, agency_repo)
        await agent_repo.update(agent, {"is_approved": False})

        payload = {"email": agent.email, "password": "testtest"}

        response = await client.post("/agents/login", data=dumps(payload))
        response_status = response.status_code
        response_json = response.json()
        response_reason = response_json["reason"]

        awaitable_status = 400
        awaitable_reason = "agent_not_approved"

        assert response_status == awaitable_status
        assert response_reason == awaitable_reason

    async def test_one_time_success(self, client, mocker, hasher, agency, agent_repo, agency_repo):
        agent = await self._register(client, mocker, agency, agent_repo, agency_repo)
        mocker.patch("src.agents.use_cases.ProcessLoginCase._remove_change_password_permission")
        await agent_repo.update(agent, {"one_time_password": hasher.hash("testtesttest")})

        payload = {"email": agent.email.upper(), "password": "testtesttest"}
        response = await client.post("/agents/login", data=dumps(payload))
        response_status = response.status_code

        agent = await agent_repo.retrieve({"id": agent.id})

        awaitable_status = 200

        assert agent.reset_time is not None
        assert response_status == awaitable_status

    async def test_one_time_fail(self, client, mocker, hasher, agency, agent_repo, agency_repo):
        agent = await self._register(client, mocker, agency, agent_repo, agency_repo)
        mocker.patch("src.agents.use_cases.ProcessLoginCase._remove_change_password_permission")
        await agent_repo.update(agent, {"one_time_password": hasher.hash("testtesttest")})

        payload = {"email": agent.email, "password": "testtesttest1"}
        response = await client.post("/agents/login", data=dumps(payload))
        response_status = response.status_code
        response_json = response.json()
        response_reason = response_json["reason"]

        agent = await agent_repo.retrieve({"id": agent.id})

        awaitable_status = 400
        awaitable_reason = "agent_password_wrong"

        assert agent.reset_time is None
        assert response_status == awaitable_status
        assert response_reason == awaitable_reason


@mark.asyncio
class TestAcceptContractView(object):
    async def test_success(self, client, agent, agent_repo, agent_authorization):
        headers = {"Authorization": agent_authorization}
        payload = {"is_contracted": True}

        assert agent.is_contracted is False

        response = await client.patch("/agents/accept", headers=headers, data=dumps(payload))
        response_status = response.status_code

        repres = await agent_repo.retrieve({"id": agent.id})

        awaitable_status = 204

        assert repres.is_contracted is True
        assert response_status == awaitable_status


@mark.asyncio
class TestRepresesAgentsListView(object):
    async def test_success(
        self,
        client,
        repres,
        agent_factory,
        repres_authorization,
        agent,
        active_agency,
        booking_factory,
        property,
        user_factory,
    ):
        other_agent = agent
        for i in range(1):
            agent = await agent_factory(agency_id=active_agency.id)
            for _ in range(i + 2):
                user = await user_factory(agency_id=active_agency.id)
        await booking_factory(
            agent_id=agent.id,
            agency_id=active_agency.id,
            active=True,
            user_id=user.id,
            property=property,
            decremented=False,
            amocrm_substage=BookingSubstages.BOOKING,
        )
        await booking_factory(
            agent_id=other_agent.id,
            agency_id=active_agency.id,
            active=True,
            user_id=user.id,
            property=property,
            decremented=False,
            amocrm_substage=BookingSubstages.MONEY_PROCESS,
        )

        headers = {"Authorization": repres_authorization}

        response = await client.get("/agents/represes", headers=headers)
        response_status = response.status_code
        response_json = response.json()
        response_count = response_json["count"]
        other_response_agent = response_json["result"][-1]
        response_agent = response_json["result"][0]
        response_clients = response_agent["active_clients"]
        response_succeed_clients = clients = response_agent["succeed_clients"]
        other_response_clients = other_response_agent["active_clients"]
        other_response_succeed_clients = other_response_agent["succeed_clients"]

        awaitable_status = 200
        awaitable_count = 2

        assert response_status == awaitable_status
        assert response_count == awaitable_count
        assert response_clients == 1
        assert response_succeed_clients == 0
        assert other_response_clients == 0
        assert other_response_succeed_clients == 1

    async def test_not_authorized(self, client, repres, agent_factory):
        for i in range(15):
            await agent_factory(agency_id=repres.agency_id)

        response = await client.get("/agents/represes")
        response_status = response.status_code

        awaitable_status = 401

        assert response_status == awaitable_status

    async def test_wrong_type(self, client, repres, agent_factory, agent_authorization):
        for i in range(15):
            await agent_factory(agency_id=repres.agency_id)

        headers = {"Authorization": agent_authorization}

        response = await client.get("/agents/represes", headers=headers)
        response_status = response.status_code

        awaitable_status = 403

        assert response_status == awaitable_status

    async def test_search_filter_success(self, client, repres, agent_factory, repres_authorization):
        for i in range(15):
            agent = await agent_factory(agency_id=repres.agency_id)

        email = agent.email

        headers = {"Authorization": repres_authorization}

        response = await client.get(f"/agents/represes?search={email}", headers=headers)
        response_status = response.status_code
        response_json = response.json()
        response_count = response_json["count"]

        awaitable_status = 200
        awaitable_count = 1

        assert response_status == awaitable_status
        assert response_count == awaitable_count

    async def test_search_filter_fail(self, client, repres, agent_factory, repres_authorization):
        for i in range(15):
            agent = await agent_factory(agency_id=repres.agency_id)

        email = agent.email

        headers = {"Authorization": repres_authorization}

        response = await client.get(f"/agents/represes?search={email}fdfd", headers=headers)
        response_status = response.status_code
        response_json = response.json()
        response_count = response_json["count"]

        awaitable_status = 200
        awaitable_count = 0

        assert response_status == awaitable_status
        assert response_count == awaitable_count


@mark.asyncio
class TestRepresesAgentsLookupView(object):
    async def test_success(self, client, repres, agent_factory, repres_authorization):
        for _ in range(15):
            await agent_factory(agency_id=repres.agency_id)

        headers = {"Authorization": repres_authorization}

        response = await client.get("/agents/represes/lookup", headers=headers)
        response_status = response.status_code
        response_json = response.json()
        response_result = response_json["result"]

        awaitable_status = 200
        awaitable_result_len = 15

        assert response_status == awaitable_status
        assert len(response_result) == awaitable_result_len

        response = await client.get("/agents/represes/lookup?search=fsdfsdfsdfsd", headers=headers)
        response_status = response.status_code
        response_json = response.json()
        response_result = response_json["result"]

        awaitable_status = 200
        awaitable_result_len = 0

        assert response_status == awaitable_status
        assert len(response_result) == awaitable_result_len

    async def test_name_search(self, client, repres, agent_factory, repres_authorization):
        for _ in range(15):
            await agent_factory(agency_id=repres.agency_id)

        headers = {"Authorization": repres_authorization}

        response = await client.get("/agents/represes/lookup?search=тест+тест", headers=headers)
        response_status = response.status_code
        response_json = response.json()
        response_type = response_json["type"]["value"]

        awaitable_status = 200
        awaitable_type = "name"

        assert response_status == awaitable_status
        assert response_type == awaitable_type

    async def test_email_search(self, client, repres, agent_factory, repres_authorization):
        for _ in range(15):
            await agent_factory(agency_id=repres.agency_id)

        headers = {"Authorization": repres_authorization}

        response = await client.get("/agents/represes/lookup?search=fsdfsdfsdfsd", headers=headers)
        response_status = response.status_code
        response_json = response.json()
        response_type = response_json["type"]["value"]

        awaitable_status = 200
        awaitable_type = "email"

        assert response_status == awaitable_status
        assert response_type == awaitable_type

    async def test_phone_search(self, client, repres, agent_factory, repres_authorization):
        for _ in range(15):
            await agent_factory(agency_id=repres.agency_id)

        headers = {"Authorization": repres_authorization}

        response = await client.get("/agents/represes/lookup?search=7928", headers=headers)
        response_status = response.status_code
        response_json = response.json()
        response_type = response_json["type"]["value"]

        awaitable_status = 200
        awaitable_type = "phone"

        assert response_status == awaitable_status
        assert response_type == awaitable_type

    async def test_unauthorized(self, client, repres, agent_factory):
        for _ in range(15):
            await agent_factory(agency_id=repres.agency_id)

        response = await client.get("/agents/represes/lookup")
        response_status = response.status_code

        awaitable_status = 401

        assert response_status == awaitable_status


@mark.asyncio
class TestRepresesAgentsRetrieveView(object):
    async def _reg_booking(self, substage, agent, booking_factory, user_factory, property):
        user = await user_factory(agent_id=agent.id)
        return await booking_factory(
            agent_id=agent.id,
            agency_id=agent.agency_id,
            active=True,
            user_id=user.id,
            property=property,
            decremented=False,
            amocrm_substage=substage,
        )

    async def test_success(
        self,
        client,
        repres,
        repres_authorization,
        user_factory,
        agent_factory,
        admin_authorization,
        booking_factory,
        property,
    ):
        agent1 = await agent_factory(agency_id=repres.agency_id)
        agent2 = await agent_factory()
        reg = partial(
            self._reg_booking,
            booking_factory=booking_factory,
            property=property,
            user_factory=user_factory,
        )

        await reg(substage=BookingSubstages.BOOKING, agent=agent1)
        await reg(substage=BookingSubstages.BOOKING, agent=agent1)
        await reg(substage=BookingSubstages.REALIZED, agent=agent1)
        await reg(substage=BookingSubstages.REALIZED, agent=agent1)
        await reg(substage=BookingSubstages.REALIZED, agent=agent1)
        await reg(substage=BookingSubstages.UNREALIZED, agent=agent1)

        await reg(substage=BookingSubstages.BOOKING, agent=agent2)
        await reg(substage=BookingSubstages.BOOKING, agent=agent2)
        await reg(substage=BookingSubstages.REALIZED, agent=agent2)
        await reg(substage=BookingSubstages.REALIZED, agent=agent2)
        await reg(substage=BookingSubstages.REALIZED, agent=agent2)
        await reg(substage=BookingSubstages.UNREALIZED, agent=agent2)

        awaitable_active_clients = 2
        awaitable_succeed_clients = 3
        awaitable_closed_clients = 1

        headers = {"Authorization": repres_authorization}

        response = await client.get(f"/agents/represes/{agent1.id}", headers=headers)
        response_status = response.status_code

        awaitable_status = 200

        assert response_status == awaitable_status

        response_data = loads(response.text)

        assert response_data

        assert response_data["closed_clients"] == awaitable_closed_clients
        assert response_data["active_clients"] == awaitable_active_clients
        assert response_data["succeeded_clients"] == awaitable_succeed_clients

    async def test_unauthorized(self, client, repres, user_factory, agent_factory):
        agent = await agent_factory(agency_id=repres.agency_id)
        for _ in range(15):
            await user_factory(agent_id=agent.id, agency_id=repres.agency_id)

        response = await client.get(f"/agents/represes/{agent.id}12")
        response_status = response.status_code

        awaitable_status = 401

        assert response_status == awaitable_status

    async def test_not_found(
        self, client, repres, user_factory, agent_factory, repres_authorization
    ):
        agent = await agent_factory(agency_id=repres.agency_id)
        for _ in range(15):
            await user_factory(agent_id=agent.id, agency_id=repres.agency_id)

        headers = {"Authorization": repres_authorization}

        response = await client.get(f"/agents/represes/{agent.id}12", headers=headers)
        response_status = response.status_code
        response_json = response.json()
        response_reason = response_json["reason"]

        awaitable_status = 404
        awaitable_reason = "agent_not_found"

        assert response_status == awaitable_status
        assert response_reason == awaitable_reason


@mark.asyncio
class TestRepresesAgentsRegisterView(object):
    async def test_success(self, client, mocker, repres, agent_repo, repres_authorization):
        mocker.patch("src.agents.api.agent.messages.SmsService.__call__")
        mocker.patch("src.agents.api.agent.messages.SmsService.as_task")
        mocker.patch("src.agents.api.agent.messages.SmsService.as_future")
        create_contact_service_mock = mocker.patch(
            "src.agents.api.agent.services.CreateContactService.__call__"
        )
        create_contact_service_mock.return_value = (-1, [])
        mocker.patch("src.agents.api.agent.services.EnsureBrokerTagService.__call__")
        mocker.patch("src.agents.api.agent.agents_tasks.import_clients_task")

        headers = {"Authorization": repres_authorization}

        payload = {
            "name": "test",
            "surname": "test",
            "patronymic": "test",
            "phone": "+79115553535",
            "email": "buba@gmail.com",
        }

        response = await client.post(
            "/agents/represes/register", headers=headers, data=dumps(payload)
        )
        response_status = response.status_code
        response_json = response.json()
        response_id = response_json["id"]

        agent = await agent_repo.retrieve({"id": response_id})

        awaitable_status = 201
        awaitable_type = "agent"

        assert agent is not None
        assert agent.is_approved is True
        assert agent.type == awaitable_type
        assert agent.agency_id == repres.agency_id
        assert agent.one_time_password is not None
        assert response_status == awaitable_status

    async def test_deleted_is_overridden(
        self, client, mocker, repres, agent_repo, repres_authorization
    ):
        # Первичная регистрация агента
        mocker.patch("src.agents.api.agent.messages.SmsService.__call__")
        mocker.patch("src.agents.api.agent.messages.SmsService.as_task")
        mocker.patch("src.agents.api.agent.messages.SmsService.as_future")
        create_contact_service_mock = mocker.patch(
            "src.agents.api.agent.services.CreateContactService.__call__"
        )
        create_contact_service_mock.return_value = (-1, [])
        mocker.patch("src.agents.api.agent.services.EnsureBrokerTagService.__call__")
        mocker.patch("src.agents.api.agent.agents_tasks.import_clients_task")

        headers = {"Authorization": repres_authorization}

        payload = {
            "name": "test",
            "surname": "test",
            "patronymic": "test",
            "phone": "+79115553535",
            "email": "buba@gmail.com",
        }

        response = await client.post(
            "/agents/represes/register", headers=headers, data=dumps(payload)
        )
        response_status = response.status_code
        response_json = response.json()
        response_id = response_json["id"]

        agent = await agent_repo.retrieve({"id": response_id})

        awaitable_status = 201
        awaitable_type = "agent"

        assert agent is not None
        assert agent.is_approved is True
        assert agent.type == awaitable_type
        assert agent.agency_id == repres.agency_id
        assert agent.one_time_password is not None
        assert response_status == awaitable_status

        # Помечаем агента как удалённого, после чего ещё раз регаем
        await agent_repo.update(agent, data=dict(is_deleted=True))

        payload = {
            "name": "test",
            "surname": "test",
            "patronymic": "test",
            "phone": "+79115553535",
            "email": "buba@gmail.com",
        }

        response = await client.post(
            "/agents/represes/register", headers=headers, data=dumps(payload)
        )
        response_status = response.status_code
        response_json = response.json()
        response_id = response_json["id"]

        agent = await agent_repo.retrieve({"id": response_id})

        awaitable_status = 201
        awaitable_type = "agent"

        assert agent is not None
        assert agent.is_approved is True
        assert agent.type == awaitable_type
        assert agent.agency_id == repres.agency_id
        assert agent.one_time_password is not None
        assert response_status == awaitable_status

    async def test_fail(
        self, client, mocker, repres, agent_repo, agent_factory, repres_authorization
    ):
        mocker.patch("src.agents.api.agent.messages.SmsService.__call__")
        mocker.patch("src.agents.api.agent.messages.SmsService.as_task")
        mocker.patch("src.agents.api.agent.messages.SmsService.as_future")
        mocker.patch("src.agents.api.agent.services.CreateContactService.__call__")

        agent = await agent_factory()

        headers = {"Authorization": repres_authorization}

        payload = {
            "name": "test",
            "surname": "test",
            "patronymic": "test",
            "phone": agent.phone,
            "email": "buba@gmail.com",
        }

        response = await client.post(
            "/agents/represes/register", headers=headers, data=dumps(payload)
        )
        response_status = response.status_code
        response_json = response.json()
        response_reason = response_json["reason"]

        awaitable_status = 400
        awaitable_reason = "agent_data_taken"

        assert response_status == awaitable_status
        assert response_reason == awaitable_reason

    async def test_unauthorized(self, client, mocker, repres, agent_repo):
        mocker.patch("src.agents.api.agent.messages.SmsService.__call__")
        mocker.patch("src.agents.api.agent.messages.SmsService.as_task")
        mocker.patch("src.agents.api.agent.messages.SmsService.as_future")
        mocker.patch("src.agents.api.agent.services.CreateContactService.__call__")

        payload = {
            "name": "test",
            "surname": "test",
            "patronymic": "test",
            "phone": "+79115553535",
            "email": "buba@gmail.com",
        }

        response = await client.post("/agents/represes/register", data=dumps(payload))
        response_status = response.status_code

        awaitable_status = 401

        assert response_status == awaitable_status


@mark.asyncio
class TestRepresesAgentsApprovalView(object):
    async def test_success(
        self, client, mocker, repres, agent_repo, agent_factory, repres_authorization
    ):
        create_contact_service_mock = mocker.patch(
            "src.agents.api.agent.services.CreateContactService.__call__"
        )
        create_contact_service_mock.return_value = (-1, [])
        mocker.patch("src.agents.api.agent.services.EnsureBrokerTagService.__call__")
        mocker.patch("src.agents.api.agent.agents_tasks.import_clients_task")
        email = mocker.patch("src.agencies.api.agency.email.EmailService.as_task")
        agent = await agent_factory(agency_id=repres.agency_id)

        headers = {"Authorization": repres_authorization}

        payload = {"is_approved": False}

        response = await client.patch(
            f"/agents/represes/approval/{agent.id}", headers=headers, data=dumps(payload)
        )
        response_status = response.status_code

        agent = await agent_repo.retrieve({"id": agent.id})

        awaitable_status = 204

        assert agent.is_approved is False
        assert response_status == awaitable_status
        email.assert_not_called()

        payload = {"is_approved": True}
        email.reset_mock()

        response = await client.patch(
            f"/agents/represes/approval/{agent.id}", headers=headers, data=dumps(payload)
        )
        response_status = response.status_code

        agent = await agent_repo.retrieve({"id": agent.id})

        awaitable_status = 204

        assert agent.is_approved is True
        assert response_status == awaitable_status
        email.assert_called_once_with()

    async def test_not_found(self, client, mocker, repres, agent_factory, repres_authorization):
        mocker.patch("src.agents.api.agent.services.CreateContactService.__call__")
        agent = await agent_factory(agency_id=repres.agency_id)

        headers = {"Authorization": repres_authorization}

        payload = {"is_approved": False}

        response = await client.patch(
            f"/agents/represes/approval/{agent.id}12", headers=headers, data=dumps(payload)
        )
        response_status = response.status_code
        response_json = response.json()
        response_reason = response_json["reason"]

        awaitable_status = 404
        awaitable_reason = "agent_not_found"

        assert response_status == awaitable_status
        assert response_reason == awaitable_reason

    async def test_unauthorized(self, client, mocker, repres, agent_factory):
        mocker.patch("src.agents.api.agent.services.CreateContactService.__call__")
        agent = await agent_factory(agency_id=repres.agency_id)

        payload = {"is_approved": False}

        response = await client.patch(f"/agents/represes/approval/{agent.id}", data=dumps(payload))
        response_status = response.status_code

        awaitable_status = 401

        assert response_status == awaitable_status


@mark.asyncio
class TestAdminsAgentsListView(object):
    async def test_success(
        self,
        client,
        agent_factory,
        active_agency,
        admin_authorization,
        user_factory,
        booking_factory,
        property,
        agent,
    ):
        other_agent = agent
        for i in range(1):
            agent = await agent_factory(agency_id=active_agency.id)
            for _ in range(i + 2):
                user = await user_factory(agency_id=active_agency.id)
        await booking_factory(
            agent_id=agent.id,
            agency_id=active_agency.id,
            active=True,
            user_id=user.id,
            property=property,
            decremented=False,
            amocrm_substage=BookingSubstages.BOOKING,
        )
        await booking_factory(
            agent_id=other_agent.id,
            agency_id=active_agency.id,
            active=True,
            user_id=user.id,
            property=property,
            decremented=False,
            amocrm_substage=BookingSubstages.MONEY_PROCESS,
        )
        headers = {"Authorization": admin_authorization}

        response = await client.get("/agents/admins", headers=headers)
        response_status = response.status_code
        response_json = response.json()
        response_count = response_json["count"]
        other_response_agent = response_json["result"][-1]
        response_agent = response_json["result"][0]
        response_clients = response_agent["active_clients"]
        response_succeed_clients = clients = response_agent["succeed_clients"]
        other_response_clients = other_response_agent["active_clients"]
        other_response_succeed_clients = other_response_agent["succeed_clients"]

        awaitable_status = 200
        awaitable_count = 2

        assert response_status == awaitable_status
        assert response_count == awaitable_count
        assert response_clients == 1
        assert response_succeed_clients == 0
        assert other_response_clients == 0
        assert other_response_succeed_clients == 1

    async def test_not_authorized(self, client, agent_factory):
        for i in range(15):
            await agent_factory()

        response = await client.get("/agents/admins")
        response_status = response.status_code

        awaitable_status = 401

        assert response_status == awaitable_status

    async def test_wrong_type(self, client, agent_factory, agent_authorization):
        for i in range(15):
            await agent_factory()

        headers = {"Authorization": agent_authorization}

        response = await client.get("/agents/admins", headers=headers)
        response_status = response.status_code

        awaitable_status = 403

        assert response_status == awaitable_status

    async def test_search_filter_success(self, client, agent_factory, admin_authorization):
        for i in range(15):
            agent = await agent_factory()

        email = agent.email

        headers = {"Authorization": admin_authorization}

        response = await client.get(f"/agents/admins?search={email}", headers=headers)
        response_status = response.status_code
        response_json = response.json()
        response_count = response_json["count"]

        awaitable_status = 200
        awaitable_count = 1

        assert response_status == awaitable_status
        assert response_count == awaitable_count

    async def test_search_filter_fail(self, client, agent_factory, admin_authorization):
        for i in range(15):
            agent = await agent_factory()

        email = agent.email

        headers = {"Authorization": admin_authorization}

        response = await client.get(f"/agents/admins?search={email}df", headers=headers)
        response_status = response.status_code
        response_json = response.json()
        response_count = response_json["count"]

        awaitable_status = 200
        awaitable_count = 0

        assert response_status == awaitable_status
        assert response_count == awaitable_count

    async def test_agency_filter(
        self, client, agent_factory, admin_authorization, agency, active_agency
    ):
        await agent_factory(agency_id=agency.id)
        await agent_factory(agency_id=active_agency.id)
        print(active_agency.id, agency.id)

        headers = {"Authorization": admin_authorization}

        response = await client.get(f"/agents/admins?agency={agency.id}", headers=headers)
        response_status = response.status_code
        response_json = response.json()
        response_count = response_json["count"]

        awaitable_status = 200
        awaitable_count = 1

        assert response_status == awaitable_status
        assert response_count == awaitable_count


@mark.asyncio
class TestAdminsAgentsLookupView(object):
    async def test_success(self, client, agent_factory, admin_authorization):
        for _ in range(31):
            await agent_factory()

        headers = {"Authorization": admin_authorization}

        response = await client.get("/agents/admins/lookup", headers=headers)
        response_status = response.status_code
        response_json = response.json()
        response_result = response_json["result"]

        awaitable_status = 200
        awaitable_result_len = 31

        assert response_status == awaitable_status
        assert len(response_result) == awaitable_result_len

        response = await client.get("/agents/admins/lookup?search=fsdfsdfsdfsd", headers=headers)
        response_status = response.status_code
        response_json = response.json()
        response_result = response_json["result"]

        awaitable_status = 200
        awaitable_result_len = 0

        assert response_status == awaitable_status
        assert len(response_result) == awaitable_result_len

    async def test_name_search(self, client, agent_factory, admin_authorization):
        for _ in range(15):
            await agent_factory()

        headers = {"Authorization": admin_authorization}

        response = await client.get("/agents/admins/lookup?search=тест+тест", headers=headers)
        response_status = response.status_code
        response_json = response.json()
        response_type = response_json["type"]["value"]

        awaitable_status = 200
        awaitable_type = "name"

        assert response_status == awaitable_status
        assert response_type == awaitable_type

    async def test_email_search(self, client, agent_factory, admin_authorization):
        for _ in range(15):
            await agent_factory()

        headers = {"Authorization": admin_authorization}

        response = await client.get("/agents/admins/lookup?search=fsdfsdfsdfsd", headers=headers)
        response_status = response.status_code
        response_json = response.json()
        response_type = response_json["type"]["value"]

        awaitable_status = 200
        awaitable_type = "email"

        assert response_status == awaitable_status
        assert response_type == awaitable_type

    async def test_phone_search(self, client, agent_factory, admin_authorization):
        for _ in range(15):
            await agent_factory()

        headers = {"Authorization": admin_authorization}

        response = await client.get("/agents/admins/lookup?search=7928", headers=headers)
        response_status = response.status_code
        response_json = response.json()
        response_type = response_json["type"]["value"]

        awaitable_status = 200
        awaitable_type = "phone"

        assert response_status == awaitable_status
        assert response_type == awaitable_type

    async def test_unauthorized(self, client, agent_factory):
        for _ in range(15):
            await agent_factory()

        response = await client.get("/agents/admins/lookup")
        response_status = response.status_code

        awaitable_status = 401

        assert response_status == awaitable_status


@mark.asyncio
class TestAdminsAgentsRetrieveView(object):
    async def _reg_booking(self, substage, agent, booking_factory, user_factory, property):
        user = await user_factory(agent_id=agent.id)
        return await booking_factory(
            agent_id=agent.id,
            agency_id=agent.agency_id,
            active=True,
            user_id=user.id,
            property=property,
            decremented=False,
            amocrm_substage=substage,
        )

    async def test_success(
        self,
        client,
        user_factory,
        agent_factory,
        admin_authorization,
        booking_factory,
        property,
    ):

        agent1 = await agent_factory()
        agent2 = await agent_factory()
        reg = partial(
            self._reg_booking,
            booking_factory=booking_factory,
            property=property,
            user_factory=user_factory,
        )

        await reg(substage=BookingSubstages.BOOKING, agent=agent1)
        await reg(substage=BookingSubstages.BOOKING, agent=agent1)
        await reg(substage=BookingSubstages.REALIZED, agent=agent1)
        await reg(substage=BookingSubstages.REALIZED, agent=agent1)
        await reg(substage=BookingSubstages.REALIZED, agent=agent1)
        await reg(substage=BookingSubstages.UNREALIZED, agent=agent1)

        await reg(substage=BookingSubstages.BOOKING, agent=agent2)
        await reg(substage=BookingSubstages.BOOKING, agent=agent2)
        await reg(substage=BookingSubstages.REALIZED, agent=agent2)
        await reg(substage=BookingSubstages.REALIZED, agent=agent2)
        await reg(substage=BookingSubstages.REALIZED, agent=agent2)
        await reg(substage=BookingSubstages.UNREALIZED, agent=agent2)

        awaitable_active_clients = 2
        awaitable_succeed_clients = 3
        awaitable_closed_clients = 1

        headers = {"Authorization": admin_authorization}

        response = await client.get(f"/agents/admins/{agent1.id}", headers=headers)
        response_status = response.status_code

        awaitable_status = 200

        response_data = loads(response.text)

        assert response_status == awaitable_status

        assert response_data["closed_clients"] == awaitable_closed_clients
        assert response_data["active_clients"] == awaitable_active_clients
        assert response_data["succeeded_clients"] == awaitable_succeed_clients

    async def test_unauthorized(self, client, user_factory, agent_factory):
        agent = await agent_factory()
        for _ in range(15):
            await user_factory(agent_id=agent.id)

        response = await client.get(f"/agents/admins/{agent.id}12")
        response_status = response.status_code

        awaitable_status = 401

        assert response_status == awaitable_status

    async def test_not_found(self, client, user_factory, agent_factory, admin_authorization):
        agent = await agent_factory()
        for _ in range(15):
            await user_factory(agent_id=agent.id)

        headers = {"Authorization": admin_authorization}

        response = await client.get(f"/agents/admins/{agent.id}12", headers=headers)
        response_status = response.status_code
        response_json = response.json()
        response_reason = response_json["reason"]

        awaitable_status = 404
        awaitable_reason = "agent_not_found"

        assert response_status == awaitable_status
        assert response_reason == awaitable_reason


@mark.asyncio
class TestAdminsAgentsRegisterView(object):
    async def test_success(self, client, mocker, agent_repo, active_agency, admin_authorization):
        mocker.patch("src.agents.api.agent.messages.SmsService.__call__")
        mocker.patch("src.agents.api.agent.messages.SmsService.as_task")
        mocker.patch("src.agents.api.agent.messages.SmsService.as_future")
        create_contact_service_mock = mocker.patch(
            "src.agents.api.agent.services.CreateContactService.__call__"
        )
        create_contact_service_mock.return_value = (-1, [])
        mocker.patch("src.agents.api.agent.services.EnsureBrokerTagService.__call__")
        mocker.patch("src.agents.api.agent.agents_tasks.import_clients_task")

        headers = {"Authorization": admin_authorization}

        payload = {
            "name": "test",
            "surname": "test",
            "patronymic": "test",
            "phone": "+79115553535",
            "email": "buba@gmail.com",
            "agency_id": active_agency.id,
        }

        response = await client.post(
            "/agents/admins/register", headers=headers, data=dumps(payload)
        )
        response_status = response.status_code
        response_json = response.json()
        response_id = response_json["id"]

        agent = await agent_repo.retrieve({"id": response_id})

        awaitable_status = 201
        awaitable_type = "agent"

        assert agent is not None
        assert agent.is_approved is True
        assert agent.type == awaitable_type
        assert agent.agency_id == active_agency.id
        assert agent.one_time_password is not None
        assert response_status == awaitable_status

    async def test_deleted_agent_is_overridden(
        self, client, mocker, agent_repo, active_agency, admin_authorization
    ):
        # Первичная регистрация
        mocker.patch("src.agents.api.agent.messages.SmsService.__call__")
        mocker.patch("src.agents.api.agent.messages.SmsService.as_task")
        mocker.patch("src.agents.api.agent.messages.SmsService.as_future")
        create_contact_service_mock = mocker.patch(
            "src.agents.api.agent.services.CreateContactService.__call__"
        )
        create_contact_service_mock.return_value = (-1, [])
        mocker.patch("src.agents.api.agent.services.EnsureBrokerTagService.__call__")
        mocker.patch("src.agents.api.agent.agents_tasks.import_clients_task")

        headers = {"Authorization": admin_authorization}

        payload = {
            "name": "test",
            "surname": "test",
            "patronymic": "test",
            "phone": "+79115553535",
            "email": "buba@gmail.com",
            "agency_id": active_agency.id,
        }

        response = await client.post(
            "/agents/admins/register", headers=headers, data=dumps(payload)
        )
        response_status = response.status_code
        response_json = response.json()
        response_id = response_json["id"]

        agent = await agent_repo.retrieve({"id": response_id})

        awaitable_status = 201
        awaitable_type = "agent"

        assert agent is not None
        assert agent.is_approved is True
        assert agent.type == awaitable_type
        assert agent.agency_id == active_agency.id
        assert agent.one_time_password is not None
        assert response_status == awaitable_status

        # Помечаем агента как удалённого, после чего ещё раз регаем
        await agent_repo.update(agent, data=dict(is_deleted=True))

        payload = {
            "name": "test",
            "surname": "test",
            "patronymic": "test",
            "phone": "+79115553535",
            "email": "buba@gmail.com",
            "agency_id": active_agency.id,
        }

        response = await client.post(
            "/agents/admins/register", headers=headers, data=dumps(payload)
        )
        response_status = response.status_code
        response_json = response.json()
        response_id = response_json["id"]

        agent = await agent_repo.retrieve({"id": response_id})

        awaitable_status = 201
        awaitable_type = "agent"

        assert agent is not None
        assert agent.is_approved is True
        assert agent.type == awaitable_type
        assert agent.agency_id == active_agency.id
        assert agent.one_time_password is not None
        assert response_status == awaitable_status

    async def test_fail(
        self, client, mocker, agent_repo, active_agency, agent_factory, admin_authorization
    ):
        mocker.patch("src.agents.api.agent.messages.SmsService.__call__")
        mocker.patch("src.agents.api.agent.messages.SmsService.as_task")
        mocker.patch("src.agents.api.agent.messages.SmsService.as_future")
        mocker.patch("src.agents.api.agent.services.CreateContactService.__call__")

        agent = await agent_factory()

        headers = {"Authorization": admin_authorization}

        payload = {
            "name": "test",
            "surname": "test",
            "patronymic": "test",
            "phone": agent.phone,
            "email": "buba@gmail.com",
            "agency_id": active_agency.id,
        }

        response = await client.post(
            "/agents/admins/register", headers=headers, data=dumps(payload)
        )
        response_status = response.status_code
        response_json = response.json()
        response_reason = response_json["reason"]

        awaitable_status = 400
        awaitable_reason = "agent_data_taken"

        assert response_status == awaitable_status
        assert response_reason == awaitable_reason

    async def test_unauthorized(self, client, mocker, agent_repo, active_agency):
        mocker.patch("src.agents.api.agent.messages.SmsService.__call__")
        mocker.patch("src.agents.api.agent.messages.SmsService.as_task")
        mocker.patch("src.agents.api.agent.messages.SmsService.as_future")
        mocker.patch("src.agents.api.agent.services.CreateContactService.__call__")

        payload = {
            "name": "test",
            "surname": "test",
            "patronymic": "test",
            "phone": "+79115553535",
            "email": "buba@gmail.com",
            "agency_id": active_agency.id,
        }

        response = await client.post("/agents/admins/register", data=dumps(payload))
        response_status = response.status_code

        awaitable_status = 401

        assert response_status == awaitable_status


@mark.asyncio
class TestAdminsAgentsApprovalView(object):
    async def test_success(self, client, mocker, agent_repo, agent_factory, admin_authorization):
        create_contact_service_mock = mocker.patch(
            "src.agents.api.agent.services.CreateContactService.__call__"
        )
        create_contact_service_mock.return_value = (-1, [])
        mocker.patch("src.agents.api.agent.services.EnsureBrokerTagService.__call__")
        mocker.patch("src.agents.api.agent.agents_tasks.import_clients_task")
        email = mocker.patch("src.agencies.api.agency.email.EmailService.as_task")
        agent = await agent_factory()

        headers = {"Authorization": admin_authorization}

        payload = {"is_approved": False}

        response = await client.patch(
            f"/agents/admins/approval/{agent.id}", headers=headers, data=dumps(payload)
        )
        response_status = response.status_code

        agent = await agent_repo.retrieve({"id": agent.id})

        awaitable_status = 204

        assert agent.is_approved is False
        assert response_status == awaitable_status
        email.assert_not_called()

        payload = {"is_approved": True}
        email.reset_mock()

        response = await client.patch(
            f"/agents/admins/approval/{agent.id}", headers=headers, data=dumps(payload)
        )
        response_status = response.status_code

        agent = await agent_repo.retrieve({"id": agent.id})

        awaitable_status = 204

        assert agent.is_approved is True
        assert response_status == awaitable_status
        email.assert_called_once_with()

    async def test_not_found(self, client, mocker, agent_factory, admin_authorization):
        mocker.patch("src.agents.api.agent.services.CreateContactService.__call__")
        agent = await agent_factory()

        headers = {"Authorization": admin_authorization}

        payload = {"is_approved": False}

        response = await client.patch(
            f"/agents/admins/approval/{agent.id}12", headers=headers, data=dumps(payload)
        )
        response_status = response.status_code
        response_json = response.json()
        response_reason = response_json["reason"]

        awaitable_status = 404
        awaitable_reason = "agent_not_found"

        assert response_status == awaitable_status
        assert response_reason == awaitable_reason

    async def test_unauthorized(self, client, mocker, agent_factory):
        mocker.patch("src.agents.api.agent.services.CreateContactService.__call__")
        agent = await agent_factory()

        payload = {"is_approved": False}

        response = await client.patch(f"/agents/admins/approval/{agent.id}", data=dumps(payload))
        response_status = response.status_code

        awaitable_status = 401

        assert response_status == awaitable_status


@mark.asyncio
class TestAdminsAgentsSpecsView(object):
    async def test_success(self, client, admin_authorization):
        headers = {"Authorization": admin_authorization}

        response = await client.get("/agents/admins/specs", headers=headers)
        response_status = response.status_code

        awaitable_status = 200

        assert response_status == awaitable_status

    async def test_unauthorized(self, client):

        response = await client.get("/agents/admins/specs")
        response_status = response.status_code

        awaitable_status = 401

        assert response_status == awaitable_status


@mark.asyncio
class TestRepresesAgentsSpecsView(object):
    async def test_success(self, client, repres_authorization):
        headers = {"Authorization": repres_authorization}

        response = await client.get("/agents/represes/specs", headers=headers)
        response_status = response.status_code

        awaitable_status = 200

        assert response_status == awaitable_status

    async def test_unauthorized(self, client):

        response = await client.get("/agents/represes/specs")
        response_status = response.status_code

        awaitable_status = 401

        assert response_status == awaitable_status


@mark.asyncio
class TestAdminsAgentsDeleteView(object):
    async def test_success(
        self,
        client,
        user_repo,
        agent_repo,
        check_repo,
        user_factory,
        agent_factory,
        active_agency,
        check_factory,
        admin_authorization,
    ):
        headers = {"Authorization": admin_authorization}

        users_ids = []
        checks_ids = []
        agent = await agent_factory()
        for i in range(5):
            user = await user_factory(agent_id=agent.id)
            if i in (2, 3):
                check = await check_factory(
                    user_id=user.id, agent_id=agent.id, agency_id=active_agency.id
                )
            else:
                check = await check_factory(user_id=user.id, agent_id=agent.id)
            users_ids.append(user.id)
            checks_ids.append(check.id)

        response = await client.delete(f"/agents/admins/{agent.id}", headers=headers)
        response_status = response.status_code

        awaitable_status = 204
        awaitable_checks_len = 2

        agent = await agent_repo.retrieve(filters={"id": agent.id})
        users = await user_repo.list(filters={"id__in": users_ids})
        checks = await check_repo.list(filters={"id__in": checks_ids})

        assert agent.is_deleted is True
        assert response_status == awaitable_status
        assert len(checks) == awaitable_checks_len
        assert all(list(u.agent_id is None for u in users))
        assert all(list(c.agent_id is None for c in checks))

    async def test_not_found(
        self,
        client,
        user_repo,
        agent_repo,
        check_repo,
        user_factory,
        agent_factory,
        active_agency,
        check_factory,
        admin_authorization,
    ):
        headers = {"Authorization": admin_authorization}

        users_ids = []
        checks_ids = []
        agent = await agent_factory()
        for i in range(5):
            user = await user_factory(agent_id=agent.id)
            if i in (2, 3):
                check = await check_factory(
                    user_id=user.id, agent_id=agent.id, agency_id=active_agency.id
                )
            else:
                check = await check_factory(user_id=user.id, agent_id=agent.id)
            users_ids.append(user.id)
            checks_ids.append(check.id)

        response = await client.delete(f"/agents/admins/{agent.id}12", headers=headers)
        response_status = response.status_code
        response_json = response.json()
        response_reason = response_json["reason"]

        awaitable_status = 404
        awaitable_reason = "agent_not_found"

        assert response_status == awaitable_status
        assert response_reason == awaitable_reason

    async def test_unauthorized(
        self,
        client,
        user_repo,
        agent_repo,
        check_repo,
        user_factory,
        agent_factory,
        active_agency,
        check_factory,
    ):

        users_ids = []
        checks_ids = []
        agent = await agent_factory()
        for i in range(5):
            user = await user_factory(agent_id=agent.id)
            if i in (2, 3):
                check = await check_factory(
                    user_id=user.id, agent_id=agent.id, agency_id=active_agency.id
                )
            else:
                check = await check_factory(user_id=user.id, agent_id=agent.id)
            users_ids.append(user.id)
            checks_ids.append(check.id)

        response = await client.delete(f"/agents/admins/{agent.id}")
        response_status = response.status_code

        awaitable_status = 401

        assert response_status == awaitable_status


@mark.asyncio
class TestRepresesAgentsDeleteView(object):
    async def test_success(
        self,
        client,
        repres,
        user_repo,
        agent_repo,
        check_repo,
        user_factory,
        agent_factory,
        active_agency,
        check_factory,
        repres_authorization,
    ):
        headers = {"Authorization": repres_authorization}

        users_ids = []
        checks_ids = []
        agent = await agent_factory(agency_id=repres.agency_id)
        for i in range(5):
            user = await user_factory(agent_id=agent.id, agency_id=agent.agency_id)
            if i in (2, 3):
                check = await check_factory(
                    user_id=user.id, agent_id=agent.id, agency_id=agent.agency_id
                )
            else:
                check = await check_factory(user_id=user.id, agent_id=agent.id)
            users_ids.append(user.id)
            checks_ids.append(check.id)

        response = await client.delete(f"/agents/represes/{agent.id}", headers=headers)
        response_status = response.status_code

        awaitable_status = 204
        awaitable_checks_len = 2

        agent = await agent_repo.retrieve(filters={"id": agent.id})
        users = await user_repo.list(filters={"id__in": users_ids})
        checks = await check_repo.list(filters={"id__in": checks_ids})

        assert agent.is_deleted is True
        assert response_status == awaitable_status
        assert len(checks) == awaitable_checks_len
        assert all(list(u.agent_id is None for u in users))
        assert all(list(c.agent_id is None for c in checks))

    async def test_not_found(
        self,
        client,
        repres,
        user_repo,
        agent_repo,
        check_repo,
        user_factory,
        agent_factory,
        active_agency,
        check_factory,
        repres_authorization,
    ):
        headers = {"Authorization": repres_authorization}

        users_ids = []
        checks_ids = []
        agent = await agent_factory(agency_id=repres.agency_id)
        for i in range(5):
            user = await user_factory(agent_id=agent.id, agency_id=agent.agency_id)
            if i in (2, 3):
                check = await check_factory(
                    user_id=user.id, agent_id=agent.id, agency_id=agent.agency_id
                )
            else:
                check = await check_factory(user_id=user.id, agent_id=agent.id)
            users_ids.append(user.id)
            checks_ids.append(check.id)

        response = await client.delete(f"/agents/represes/{agent.id}12", headers=headers)
        response_status = response.status_code
        response_json = response.json()
        response_reason = response_json["reason"]

        awaitable_status = 404
        awaitable_reason = "agent_not_found"

        assert response_status == awaitable_status
        assert response_reason == awaitable_reason

    async def test_unauthorized(
        self,
        client,
        repres,
        user_repo,
        agent_repo,
        check_repo,
        user_factory,
        agent_factory,
        active_agency,
        check_factory,
    ):

        users_ids = []
        checks_ids = []
        agent = await agent_factory(agency_id=repres.agency_id)
        for i in range(5):
            user = await user_factory(agent_id=agent.id, agency_id=agent.agency_id)
            if i in (2, 3):
                check = await check_factory(
                    user_id=user.id, agent_id=agent.id, agency_id=agent.agency_id
                )
            else:
                check = await check_factory(user_id=user.id, agent_id=agent.id)
            users_ids.append(user.id)
            checks_ids.append(check.id)

        response = await client.delete(f"/agents/represes/{agent.id}")
        response_status = response.status_code

        awaitable_status = 401

        assert response_status == awaitable_status


@mark.asyncio
class TestAgentAdminsUpdateView(object):
    async def test_success(self, client, agent, mocker, agent_repo, admin_authorization):
        mocker.patch("src.agents.api.agent.messages.SmsService.__call__")
        mocker.patch("src.agents.api.agent.messages.SmsService.as_task")
        mocker.patch("src.agents.api.agent.messages.SmsService.as_future")
        mocker.patch("src.agents.api.agent.email.EmailService.__call__")
        mocker.patch("src.agents.api.agent.email.EmailService.as_task")
        mocker.patch("src.agents.api.agent.email.EmailService.as_future")

        payload = {
            "name": "test",
            "surname": "test",
            "patronymic": "test",
            "phone": "+79998000017",
            "email": "lupa_and_pupa@mail.ru",
        }

        headers = {"Authorization": admin_authorization}

        response = await client.patch(
            f"/agents/admins/{agent.id}", data=dumps(payload), headers=headers
        )
        response_status = response.status_code

        awaitable_status = 204

        agent = await agent_repo.retrieve(filters={"id": agent.id})

        assert agent.change_phone
        assert agent.change_email
        assert agent.change_phone_token
        assert agent.change_email_token
        assert response_status == awaitable_status

    async def test_agent_not_found(self, client, agent, mocker, agent_repo, admin_authorization):
        mocker.patch("src.agents.api.agent.messages.SmsService.__call__")
        mocker.patch("src.agents.api.agent.messages.SmsService.as_task")
        mocker.patch("src.agents.api.agent.messages.SmsService.as_future")
        mocker.patch("src.agents.api.agent.email.EmailService.__call__")
        mocker.patch("src.agents.api.agent.email.EmailService.as_task")
        mocker.patch("src.agents.api.agent.email.EmailService.as_future")

        payload = {
            "name": "test",
            "surname": "test",
            "patronymic": "test",
            "phone": "+79998000017",
            "email": "lupa_and_pupa@mail.ru",
        }

        headers = {"Authorization": admin_authorization}

        response = await client.patch(
            f"/agents/admins/{agent.id}12", data=dumps(payload), headers=headers
        )
        response_status = response.status_code
        response_json = response.json()
        response_reason = response_json["reason"]

        awaitable_status = 404
        awaitable_reason = "agent_not_found"

        assert response_status == awaitable_status
        assert response_reason == awaitable_reason

    async def test_phone_taken(self, client, agent, admin, mocker, agent_repo, admin_authorization):
        mocker.patch("src.agents.api.agent.messages.SmsService.__call__")
        mocker.patch("src.agents.api.agent.messages.SmsService.as_task")
        mocker.patch("src.agents.api.agent.messages.SmsService.as_future")
        mocker.patch("src.agents.api.agent.email.EmailService.__call__")
        mocker.patch("src.agents.api.agent.email.EmailService.as_task")
        mocker.patch("src.agents.api.agent.email.EmailService.as_future")

        payload = {
            "name": "test",
            "surname": "test",
            "patronymic": "test",
            "phone": admin.phone,
            "email": "lupa_and_pupa@mail.ru",
        }

        headers = {"Authorization": admin_authorization}

        response = await client.patch(
            f"/agents/admins/{agent.id}", data=dumps(payload), headers=headers
        )
        response_status = response.status_code
        response_json = response.json()
        response_reason = response_json["reason"]

        awaitable_status = 400
        awaitable_reason = "agent_phone_taken"

        assert response_status == awaitable_status
        assert response_reason == awaitable_reason

    async def test_email_taken(self, client, agent, admin, mocker, agent_repo, admin_authorization):
        mocker.patch("src.agents.api.agent.messages.SmsService.__call__")
        mocker.patch("src.agents.api.agent.messages.SmsService.as_task")
        mocker.patch("src.agents.api.agent.messages.SmsService.as_future")
        mocker.patch("src.agents.api.agent.email.EmailService.__call__")
        mocker.patch("src.agents.api.agent.email.EmailService.as_task")
        mocker.patch("src.agents.api.agent.email.EmailService.as_future")

        payload = {
            "name": "test",
            "surname": "test",
            "patronymic": "test",
            "phone": "+79998000017",
            "email": admin.email,
        }

        headers = {"Authorization": admin_authorization}

        response = await client.patch(
            f"/agents/admins/{agent.id}", data=dumps(payload), headers=headers
        )
        response_status = response.status_code
        response_json = response.json()
        response_reason = response_json["reason"]

        awaitable_status = 400
        awaitable_reason = "agent_email_taken"

        assert response_status == awaitable_status
        assert response_reason == awaitable_reason

    async def test_unauthorized(self, client, agent):
        payload = {
            "name": "test",
            "surname": "test",
            "patronymic": "test",
            "phone": "+79998000017",
            "email": "lupa_and_pupa@mail.ru",
        }

        response = await client.patch(f"/agents/admins/{agent.id}", data=dumps(payload))
        response_status = response.status_code

        awaitable_status = 401

        assert response_status == awaitable_status


@mark.asyncio
class TestSetPasswordView(object):
    async def test_success(
        self,
        client_with_session_cookie: httpx.AsyncClient,
        agent,
        mocker,
        agent_repo,
        create_email_token,
    ):
        # email_reset
        mocker.patch("src.agents.use_cases.EmailResetCase._send_email")
        mocker.patch("src.agents.use_cases.ResetPasswordCase._remove_discard")
        mocker.patch("src.agents.use_cases.SetPasswordCase._send_email")
        payload = {"email": agent.email}

        response = await client_with_session_cookie.post("/agents/email_reset", data=dumps(payload))
        response_status = response.status_code

        agent = await agent_repo.retrieve({"id": agent.id})

        awaitable_status = 204

        assert agent.discard_token is not None
        assert response_status == awaitable_status

        # reset_password
        response = await client_with_session_cookie.get(
            "/agents/reset_password?q={}&p={}".format(
                create_email_token(agent.id), agent.discard_token
            ),
        )
        # assert response.status_code == 200  # Тут редирект на фронт broker.xxx

        # set_password
        payload = {
            "is_contracted": True,
            "password_1": "qweqweqwe",
            "password_2": "qweqweqwe",
        }
        response = await client_with_session_cookie.post(
            "/agents/set_password", data=dumps(payload)
        )
        assert response.status_code == 200
