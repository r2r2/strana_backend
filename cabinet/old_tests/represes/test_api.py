from json import dumps

import httpx
from pytest import mark
from secrets import token_urlsafe


@mark.asyncio
class TestProcessRegisterView(object):
    async def test_success(
        self,
        client,
        mocker,
        agency,
        agency_repo,
        repres_repo,
        admin_factory,
        agent_factory,
        user_factory,
        admin_repo,
        agent_repo,
        user_repo,
        image_factory,
    ):
        mocker.patch("src.represes.use_cases.ProcessRegisterCase._send_repres_confirmation_email")
        mocker.patch("src.represes.use_cases.ProcessRegisterCase._send_admins_email")
        files_mock = mocker.patch("src.agencies.api.agency.files.FileProcessor.__call__")
        files_mock.return_value = []

        file = image_factory("test.png")

        agency_payload = {"inn": "3213112312", "city": "test", "type": "OOO", "name": "borov"}
        files = {
            "inn_files": file,
            "ogrn_files": file,
            "ogrnip_files": file,
            "charter_files": file,
            "company_files": file,
            "passport_files": file,
            "procuratory_files": file,
        }

        admin = await admin_factory(email="test@gmail.com")
        agent = await agent_factory(email="test@gmail.com")
        user = await user_factory(email="test@gmail.com")
        await admin_repo.update(admin, {"is_active": True})
        await agent_repo.update(agent, {"is_active": True})
        await user_repo.update(user, {"is_active": True})
        await agency_repo.update(agency, {"is_approved": True})

        repres_payload = {
            "name": "test",
            "surname": "test",
            "patronymic": "test",
            "phone": "+78005553535",
            "password_1": "testtest",
            "password_2": "testtest",
            "email": "test@gmail.com",
            "duty_type": "director",
            "is_contracted": True,
        }

        payload = dict(repres=repres_payload, agency=agency_payload)

        response = await client.post(
            "/represes/register", data=dict(payload=dumps(payload)), files=files
        )
        assert response.status_code == 201
        assert response.json() == {
            "agency": {
                "id": 2,
                "inn": "3213112312",
                "city": "test",
                "type": {"value": "OOO", "label": "ООО"},
            },
            "repres": {"id": 4, "is_approved": True},
        }

        agency = await agency_repo.retrieve({"inn": "3213112312"})
        assert agency is not None

        repres = await repres_repo.retrieve({"phone": "+78005553535"})

        assert repres.is_active is False
        assert repres.is_approved is True
        assert repres.password is not None
        assert repres.type == "repres"
        assert repres.email_token is not None
        assert repres.duty_type == "director"
        assert repres.maintained_id == agency.id

    async def test_email_taken(
        self,
        client,
        repres,
        agency,
        repres_repo,
        agency_repo,
        admin_factory,
        agent_factory,
        user_factory,
        admin_repo,
        agent_repo,
        user_repo,
        mocker,
        image_factory,
    ):
        mocker.patch("src.represes.use_cases.ProcessRegisterCase._send_repres_confirmation_email")
        mocker.patch("src.represes.use_cases.ProcessRegisterCase._send_admins_email")
        files_mock = mocker.patch("src.agencies.api.agency.files.FileProcessor.__call__")
        files_mock.return_value = []

        file = image_factory("test.png")

        agency_payload = {"inn": "3213112312", "city": "test", "type": "OOO", "name": "borov"}
        files = {
            "inn_files": file,
            "ogrn_files": file,
            "ogrnip_files": file,
            "charter_files": file,
            "company_files": file,
            "passport_files": file,
            "procuratory_files": file,
        }

        admin = await admin_factory(email="test@gmail.com")
        agent = await agent_factory(email="test@gmail.com")
        user = await user_factory(email="test@gmail.com")
        await admin_repo.update(admin, {"is_active": True})
        await agent_repo.update(agent, {"is_active": True})
        await user_repo.update(user, {"is_active": True})

        await agency_repo.update(agency, {"is_approved": True})
        await repres_repo.update(repres, {"email": "test@gmail.com", "is_active": True})
        repres_payload = {
            "name": "test",
            "surname": "test",
            "patronymic": "test",
            "phone": "+78005553535",
            "password_1": "testtest",
            "password_2": "testtest",
            "email": "test@gmail.com",
            "duty_type": "director",
            "is_contracted": True,
        }

        payload = dict(repres=repres_payload, agency=agency_payload)
        response = await client.post(
            "/represes/register", data=dict(payload=dumps(payload)), files=files
        )
        response_status = response.status_code
        response_json = response.json()
        response_reason = response_json["reason"]

        repres = await repres_repo.retrieve({"phone": "+78005553535"})

        awaitable_status = 400
        awaitable_reason = "repres_already_registered"

        assert repres is None
        assert response_status == awaitable_status
        assert response_reason == awaitable_reason

    async def test_already_registered(
        self,
        client,
        repres,
        agency_repo,
        admin_factory,
        agent_factory,
        user_factory,
        admin_repo,
        agent_repo,
        user_repo,
        mocker,
        image_factory,
    ):
        mocker.patch("src.represes.use_cases.ProcessRegisterCase._send_repres_confirmation_email")
        mocker.patch("src.represes.use_cases.ProcessRegisterCase._send_admins_email")
        files_mock = mocker.patch("src.agencies.api.agency.files.FileProcessor.__call__")
        files_mock.return_value = []

        file = image_factory("test.png")

        agency_payload = {"inn": "3213112312", "city": "test", "type": "OOO", "name": "borov"}
        files = {
            "inn_files": file,
            "ogrn_files": file,
            "ogrnip_files": file,
            "charter_files": file,
            "company_files": file,
            "passport_files": file,
            "procuratory_files": file,
        }

        admin = await admin_factory(email=repres.email)
        agent = await agent_factory(email=repres.email)
        user = await user_factory(email=repres.email)
        await admin_repo.update(admin, {"is_active": True})
        await agent_repo.update(agent, {"is_active": True})
        await user_repo.update(user, {"is_active": True})

        # await agency_repo.update(agency, {"is_approved": True})
        repres_payload = {
            "name": repres.name,
            "surname": repres.surname,
            "patronymic": repres.patronymic,
            "phone": repres.phone,
            "password_1": "testtest",
            "password_2": "testtest",
            "email": repres.email,
            "duty_type": repres.duty_type.value,
            "is_contracted": True,
        }

        payload = dict(repres=repres_payload, agency=agency_payload)
        response = await client.post(
            "/represes/register", data=dict(payload=dumps(payload)), files=files
        )
        response_status = response.status_code
        response_json = response.json()
        response_reason = response_json["reason"]

        awaitable_status = 400
        awaitable_reason = "repres_already_registered"

        assert response_status == awaitable_status
        assert response_reason == awaitable_reason

    async def test_deleted_is_overridden(
        self,
        client,
        repres,
        agency_repo,
        admin_factory,
        agent_factory,
        user_factory,
        admin_repo,
        agent_repo,
        repres_repo,
        user_repo,
        mocker,
        image_factory,
    ):
        mocker.patch("src.represes.use_cases.ProcessRegisterCase._send_repres_confirmation_email")
        mocker.patch("src.represes.use_cases.ProcessRegisterCase._send_admins_email")
        files_mock = mocker.patch("src.agencies.api.agency.files.FileProcessor.__call__")
        files_mock.return_value = []

        admin = await admin_factory(email=repres.email)
        agent = await agent_factory(email=repres.email)
        user = await user_factory(email=repres.email)
        await admin_repo.update(admin, {"is_active": True})
        await agent_repo.update(agent, {"is_active": True})
        await user_repo.update(user, {"is_active": True})

        await agency_repo.update(await repres.agency, {"is_deleted": True})
        await repres_repo.update(repres, {"is_deleted": True})

        file = image_factory("test.png")

        agency_payload = {"inn": "3213112312", "city": "test", "type": "OOO", "name": "borov"}
        files = {
            "inn_files": file,
            "ogrn_files": file,
            "ogrnip_files": file,
            "charter_files": file,
            "company_files": file,
            "passport_files": file,
            "procuratory_files": file,
        }
        repres_payload = {
            "name": repres.name,
            "surname": repres.surname,
            "patronymic": repres.patronymic,
            "phone": repres.phone,
            "password_1": "testtest",
            "password_2": "testtest",
            "email": repres.email,
            "duty_type": repres.duty_type.value,
            "is_contracted": True,
        }

        payload = dict(repres=repres_payload, agency=agency_payload)
        response = await client.post(
            "/represes/register", data=dict(payload=dumps(payload)), files=files
        )
        assert response.status_code == 201

    async def test_repres_not_approved_raises_already_registered(
        self,
        client,
        agency,
        repres,
        agency_repo,
        repres_repo,
        admin_factory,
        agent_factory,
        user_factory,
        admin_repo,
        agent_repo,
        user_repo,
        mocker,
        image_factory,
    ):
        mocker.patch("src.represes.use_cases.ProcessRegisterCase._send_repres_confirmation_email")
        mocker.patch("src.represes.use_cases.ProcessRegisterCase._send_admins_email")
        files_mock = mocker.patch("src.agencies.api.agency.files.FileProcessor.__call__")
        files_mock.return_value = []

        file = image_factory("test.png")

        agency_payload = {"inn": "3213112312", "city": "test", "type": "OOO", "name": "borov"}
        files = {
            "inn_files": file,
            "ogrn_files": file,
            "ogrnip_files": file,
            "charter_files": file,
            "company_files": file,
            "passport_files": file,
            "procuratory_files": file,
        }

        admin = await admin_factory(email=repres.email)
        agent = await agent_factory(email=repres.email)
        user = await user_factory(email=repres.email)
        await admin_repo.update(admin, {"is_active": True})
        await agent_repo.update(agent, {"is_active": True})
        await user_repo.update(user, {"is_active": True})

        await repres_repo.update(repres, {"is_approved": False})
        await agency_repo.update(agency, {"is_approved": True})

        repres_payload = {
            "name": repres.name,
            "surname": repres.surname,
            "patronymic": repres.patronymic,
            "phone": repres.phone,
            "password_1": "testtest",
            "password_2": "testtest",
            "email": repres.email,
            "agency": agency.id,
            "duty_type": repres.duty_type.value,
            "is_contracted": True,
        }

        payload = dict(repres=repres_payload, agency=agency_payload)
        response = await client.post(
            "/represes/register", data=dict(payload=dumps(payload)), files=files
        )
        response_status = response.status_code
        response_json = response.json()
        response_reason = response_json["reason"]

        awaitable_status = 400
        awaitable_reason = "repres_already_registered"

        assert response_status == awaitable_status
        assert response_reason == awaitable_reason


@mark.asyncio
class TestConfirmEmailView(object):
    async def test_success(self, client, repres, repres_repo, create_email_token):
        await repres_repo.update(repres, {"is_active": False})
        token = create_email_token(repres.id)

        await client.get(f"/represes/confirm_email?q={token}&p={repres.email_token}")

        repres = await repres_repo.retrieve({"id": repres.id})

        assert repres.is_active is True
        assert repres.email_token is None

    async def test_fail(self, client, create_email_token, repres, repres_repo):
        await repres_repo.update(repres, {"is_active": False})
        token = create_email_token(repres.id)

        await client.get(f"/represes/confirm_email?q={token}&p={repres.email_token}12")

        repres = await repres_repo.retrieve({"id": repres.id})

        assert repres.is_active is False
        assert repres.email_token is not None

    async def test_already_active(self, client, create_email_token, repres, repres_repo):
        token = create_email_token(repres.id)

        await client.get(f"/represes/confirm_email?q={token}&p={repres.email_token}")

        repres = await repres_repo.retrieve({"id": repres.id})

        assert repres.is_active is True
        assert repres.email_token is not None


@mark.asyncio
class TestEmailResetView(object):
    async def test_success(self, client, mocker, repres, repres_repo):
        mocker.patch("src.represes.use_cases.EmailResetCase._send_email")
        payload = {"email": repres.email.upper()}

        response = await client.post("/represes/email_reset", data=dumps(payload))
        response_status = response.status_code

        repres = await repres_repo.retrieve({"id": repres.id})

        awaitable_status = 204

        assert repres.discard_token is not None
        assert response_status == awaitable_status

    async def test_not_found(self, client, repres, repres_repo):
        await repres_repo.update(repres, {"is_active": False})
        payload = {"email": repres.email}

        response = await client.post("/represes/email_reset", data=dumps(payload))
        response_status = response.status_code
        response_json = response.json()
        response_reason = response_json["reason"]

        repres = await repres_repo.retrieve({"id": repres.id})

        awaitable_status = 400
        awaitable_reason = "repres_not_found"

        assert repres.discard_token is None
        assert response_status == awaitable_status
        assert response_reason == awaitable_reason

    async def test_not_approved(self, client, repres, repres_repo):
        await repres_repo.update(repres, {"is_approved": False})
        payload = {"email": repres.email}

        response = await client.post("/represes/email_reset", data=dumps(payload))
        response_status = response.status_code
        response_json = response.json()
        response_reason = response_json["reason"]

        repres = await repres_repo.retrieve({"id": repres.id})

        awaitable_status = 400
        awaitable_reason = "repres_not_approved"

        assert repres.discard_token is None
        assert response_status == awaitable_status
        assert response_reason == awaitable_reason


@mark.asyncio
class TestResetPasswordView(object):
    async def test_success(self, client, mocker, repres, repres_repo, create_email_token):
        mocker.patch("src.represes.use_cases.ResetPasswordCase._remove_discard")
        await repres_repo.update(repres, {"discard_token": token_urlsafe(32)})

        token = create_email_token(repres.id)

        await client.get(f"/represes/reset_password?q={token}&p={repres.discard_token}")

        repres = await repres_repo.retrieve({"id": repres.id})

        assert repres.discard_token is None
        assert repres.reset_time is not None

    async def test_fail(self, client, repres_repo, repres, create_email_token):
        await repres_repo.update(repres, {"discard_token": token_urlsafe(32), "is_active": False})

        token = create_email_token(repres.id)

        await client.get(f"/represes/reset_password?q={token}&p={repres.discard_token}fsdfsd")

        repres = await repres_repo.retrieve({"id": repres.id})

        assert repres.reset_time is None
        assert repres.discard_token is not None


@mark.asyncio
class TestChangePasswordView(object):
    async def test_success(self, client, repres_authorization):
        payload = {"password_1": "testtest", "password_2": "testtest"}
        headers = {"Authorization": repres_authorization}

        response = await client.patch(
            "/represes/change_password", data=dumps(payload), headers=headers
        )
        response_status = response.status_code

        awaitable_status = 204

        assert response_status == awaitable_status

    async def test_no_repres_id(self, client):
        payload = {"password_1": "testtest", "password_2": "testtest"}

        response = await client.patch("/represes/change_password", data=dumps(payload))
        response_status = response.status_code
        response_json = response.json()
        response_reason = response_json["reason"]

        awaitable_status = 400
        awaitable_reason = "repres_change_password"

        assert response_status == awaitable_status
        assert response_reason == awaitable_reason

    async def test_no_repres(self, client, repres, repres_repo, repres_authorization):
        await repres_repo.update(repres, {"is_active": False})
        payload = {"password_1": "testtest", "password_2": "testtest"}
        headers = {"Authorization": repres_authorization}

        response = await client.patch(
            "/represes/change_password", data=dumps(payload), headers=headers
        )
        response_status = response.status_code
        response_json = response.json()
        response_reason = response_json["reason"]

        awaitable_status = 400
        awaitable_reason = "repres_change_password"

        assert response_status == awaitable_status
        assert response_reason == awaitable_reason


@mark.asyncio
class TestProcessLoginView(object):
    async def _register(self, client, mocker, agency, agency_repo, repres_repo, image_factory):
        mocker.patch("src.represes.use_cases.ProcessRegisterCase._send_repres_confirmation_email")
        mocker.patch("src.represes.use_cases.ProcessRegisterCase._send_admins_email")
        files_mock = mocker.patch("src.agencies.api.agency.files.FileProcessor.__call__")
        files_mock.return_value = []

        await agency_repo.update(agency, {"is_approved": True})

        file = image_factory("test.png")

        agency_payload = {"inn": "3213112312", "city": "test", "type": "OOO", "name": "borov"}
        files = {
            "inn_files": file,
            "ogrn_files": file,
            "ogrnip_files": file,
            "charter_files": file,
            "company_files": file,
            "passport_files": file,
            "procuratory_files": file,
        }

        repres_payload = {
            "name": "test",
            "surname": "test",
            "patronymic": "test",
            "phone": "+78005553535",
            "password_1": "testtest",
            "password_2": "testtest",
            "email": "test@gmail.com",
            "agency": agency.id,
            "duty_type": "director",
            "is_contracted": True,
        }

        payload = dict(repres=repres_payload, agency=agency_payload)
        response = await client.post(
            "/represes/register", data=dict(payload=dumps(payload)), files=files
        )
        response_json = response.json()
        response_id = response_json["repres"]["id"]

        repres = await repres_repo.retrieve({"id": response_id})
        repres = await repres_repo.update(repres, {"is_active": True, "is_approved": True})

        return repres

    async def test_success(self, client, mocker, agency, repres_repo, agency_repo, image_factory):
        repres = await self._register(
            client, mocker, agency, agency_repo, repres_repo, image_factory
        )
        mocker.patch("src.represes.use_cases.ProcessLoginCase._remove_change_password_permission")

        payload = {"email": repres.email.upper(), "password": "testtest"}

        response = await client.post("/represes/login", data=dumps(payload))
        response_status = response.status_code

        awaitable_status = 200

        assert response_status == awaitable_status

    async def test_fail(self, client, mocker, agency, repres_repo, agency_repo, image_factory):
        repres = await self._register(
            client, mocker, agency, agency_repo, repres_repo, image_factory
        )

        payload = {"email": repres.email, "password": "testtest1"}

        response = await client.post("/represes/login", data=dumps(payload))
        response_status = response.status_code
        response_json = response.json()
        response_reason = response_json["reason"]

        awaitable_status = 400
        awaitable_reason = "repres_password_wrong"

        assert response_status == awaitable_status
        assert response_reason == awaitable_reason

    async def test_not_found(self, client):
        payload = {"email": "wrong@gmail.com", "password": "testtest1"}

        response = await client.post("/represes/login", data=dumps(payload))
        response_status = response.status_code
        response_json = response.json()
        response_reason = response_json["reason"]

        awaitable_status = 400
        awaitable_reason = "repres_not_found"

        assert response_status == awaitable_status
        assert response_reason == awaitable_reason

    async def test_not_approved(
        self, client, mocker, agency, repres_repo, agency_repo, image_factory
    ):
        repres = await self._register(
            client, mocker, agency, agency_repo, repres_repo, image_factory
        )
        await repres_repo.update(repres, {"is_approved": False})

        payload = {"email": repres.email, "password": "testtest"}

        response = await client.post("/represes/login", data=dumps(payload))
        response_status = response.status_code
        response_json = response.json()
        response_reason = response_json["reason"]

        awaitable_status = 400
        awaitable_reason = "repres_not_approved"

        assert response_status == awaitable_status
        assert response_reason == awaitable_reason

    async def test_one_time_success(
        self, client, mocker, agency, hasher, repres_repo, agency_repo, image_factory
    ):
        repres = await self._register(
            client, mocker, agency, agency_repo, repres_repo, image_factory
        )
        mocker.patch("src.represes.use_cases.ProcessLoginCase._remove_change_password_permission")
        await repres_repo.update(repres, {"one_time_password": hasher.hash("testtesttest")})

        payload = {"email": repres.email, "password": "testtesttest"}
        response = await client.post("/represes/login", data=dumps(payload))
        response_status = response.status_code

        repres = await repres_repo.retrieve({"id": repres.id})

        awaitable_status = 200

        assert repres.reset_time is not None
        assert response_status == awaitable_status

    async def test_one_time_fail(
        self, client, mocker, agency, hasher, repres_repo, agency_repo, image_factory
    ):
        repres = await self._register(
            client, mocker, agency, agency_repo, repres_repo, image_factory
        )
        mocker.patch("src.represes.use_cases.ProcessLoginCase._remove_change_password_permission")
        await repres_repo.update(repres, {"one_time_password": hasher.hash("testtesttest")})

        payload = {"email": repres.email, "password": "testtesttest1"}
        response = await client.post("/represes/login", data=dumps(payload))
        response_status = response.status_code
        response_json = response.json()
        response_reason = response_json["reason"]

        repres = await repres_repo.retrieve({"id": repres.id})

        awaitable_status = 400
        awaitable_reason = "repres_password_wrong"

        assert repres.reset_time is None
        assert response_status == awaitable_status
        assert response_reason == awaitable_reason


@mark.asyncio
class TestAcceptContractView(object):
    async def test_success(self, client, repres, repres_repo, repres_authorization):
        headers = {"Authorization": repres_authorization}
        payload = {"is_contracted": True}

        assert repres.is_contracted is False

        response = await client.patch("/represes/accept", headers=headers, data=dumps(payload))
        response_status = response.status_code

        repres = await repres_repo.retrieve({"id": repres.id})

        awaitable_status = 204

        assert repres.is_contracted is True
        assert response_status == awaitable_status


@mark.asyncio
class TestSetPasswordView(object):
    async def test_success(
        self,
        client_with_session_cookie: httpx.AsyncClient,
        repres,
        mocker,
        repres_repo,
        create_email_token,
    ):
        # email_reset
        mocker.patch("src.represes.use_cases.EmailResetCase._send_email")
        mocker.patch("src.represes.use_cases.ResetPasswordCase._remove_discard")
        mocker.patch("src.represes.use_cases.SetPasswordCase._send_email")
        payload = {"email": repres.email.upper()}

        response = await client_with_session_cookie.post(
            "/represes/email_reset", data=dumps(payload)
        )
        response_status = response.status_code

        repres = await repres_repo.retrieve({"id": repres.id})

        awaitable_status = 204

        assert repres.discard_token is not None
        assert response_status == awaitable_status

        # reset_password
        response = await client_with_session_cookie.get(
            "/represes/reset_password?q={}&p={}".format(
                create_email_token(repres.id), repres.discard_token
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
            "/represes/set_password", data=dumps(payload)
        )
        assert response.status_code == 200
