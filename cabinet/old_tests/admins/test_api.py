from json import dumps

import httpx
from pytest import mark
from secrets import token_urlsafe


@mark.asyncio
class TestProcessRegisterView(object):
    async def test_success(self, client, mocker):
        mocker.patch("src.admins.api.admin.messages.SmsService.__call__")
        mocker.patch("src.admins.api.admin.messages.SmsService.as_task")
        mocker.patch("src.admins.api.admin.messages.SmsService.as_future")

        payload = {
            "name": "test",
            "surname": "test",
            "patronymic": "test",
            "phone": "+78005553535",
            "email": "test@gmail.com",
        }

        response = await client.post("/admins/register", data=dumps(payload))
        response_status = response.status_code

        awaitable_status = 201

        assert response_status == awaitable_status

    async def test_data_taken(self, client, admin):
        payload = {
            "name": "test",
            "surname": "test",
            "patronymic": "test",
            "phone": admin.phone,
            "email": admin.email.upper(),
        }

        response = await client.post("/admins/register", data=dumps(payload))
        response_status = response.status_code
        response_json = response.json()
        response_reason = response_json["reason"]

        awaitable_status = 400
        awaitable_reason = "admin_data_taken"

        assert response_status == awaitable_status
        assert response_reason == awaitable_reason


@mark.asyncio
class TestConfirmEmailView(object):
    async def test_success(self, client, admin, admin_repo, create_email_token):
        await admin_repo.update(admin, {"is_active": False})
        token = create_email_token(admin.id)

        await client.get(f"/admins/confirm_email?q={token}&p={admin.email_token}")

        admin = await admin_repo.retrieve({"id": admin.id})

        assert admin.is_active is True
        assert admin.email_token is None

    async def test_fail(self, client, admin, admin_repo, create_email_token):
        await admin_repo.update(admin, {"is_active": False})
        token = create_email_token(admin.id)

        await client.get(f"/admins/confirm_email?q={token}&p={admin.email_token}12")

        admin = await admin_repo.retrieve({"id": admin.id})

        assert admin.is_active is False
        assert admin.email_token is not None

    async def test_already_active(self, client, admin, admin_repo, create_email_token):
        token = create_email_token(admin.id)

        await client.get(f"/admins/confirm_email?q={token}&p={admin.email_token}")

        admin = await admin_repo.retrieve({"id": admin.id})

        assert admin.is_active is True
        assert admin.email_token is not None


@mark.asyncio
class TestEmailResetView(object):
    async def test_success(self, client, admin, mocker, admin_repo):
        mocker.patch("src.admins.use_cases.EmailResetCase._send_email")
        payload = {"email": admin.email.upper()}

        response = await client.post("/admins/email_reset", data=dumps(payload))
        response_status = response.status_code

        admin = await admin_repo.retrieve({"id": admin.id})

        awaitable_status = 204

        assert admin.discard_token is not None
        assert response_status == awaitable_status

    async def test_not_found(self, client, admin, admin_repo):
        await admin_repo.update(admin, {"is_active": False})
        payload = {"email": admin.email}

        response = await client.post("/admins/email_reset", data=dumps(payload))
        response_status = response.status_code
        response_json = response.json()
        response_reason = response_json["reason"]

        admin = await admin_repo.retrieve({"id": admin.id})

        awaitable_status = 404
        awaitable_reason = "admin_not_found"

        assert admin.discard_token is None
        assert response_status == awaitable_status
        assert response_reason == awaitable_reason


@mark.asyncio
class TestResetPasswordView(object):
    async def test_success(self, client, admin, mocker, admin_repo, create_email_token):
        mocker.patch("src.admins.use_cases.ResetPasswordCase._remove_discard")
        await admin_repo.update(admin, {"discard_token": token_urlsafe(32)})

        token = create_email_token(admin.id)

        await client.get(f"/admins/reset_password?q={token}&p={admin.discard_token}")

        admin = await admin_repo.retrieve({"id": admin.id})

        assert admin.discard_token is None
        assert admin.reset_time is not None

    async def test_fail(self, client, admin, admin_repo, create_email_token):
        await admin_repo.update(admin, {"discard_token": token_urlsafe(32), "is_active": False})

        token = create_email_token(admin.id)

        await client.get(f"/admins/reset_password?q={token}&p={admin.discard_token}fsdfsd")

        admin = await admin_repo.retrieve({"id": admin.id})

        assert admin.reset_time is None
        assert admin.discard_token is not None


@mark.asyncio
class TestChangePasswordView(object):
    async def test_success(self, client, admin_authorization):
        payload = {"password_1": "testtest", "password_2": "testtest"}
        headers = {"Authorization": admin_authorization}

        response = await client.patch(
            "/admins/change_password", data=dumps(payload), headers=headers
        )
        response_status = response.status_code

        awaitable_status = 204

        assert response_status == awaitable_status

    async def test_no_admin_id(self, client):
        payload = {"password_1": "testtest", "password_2": "testtest"}

        response = await client.patch("/admins/change_password", data=dumps(payload))
        response_status = response.status_code
        response_json = response.json()
        response_reason = response_json["reason"]

        awaitable_status = 400
        awaitable_reason = "admin_change_password"

        assert response_status == awaitable_status
        assert response_reason == awaitable_reason

    async def test_no_admin(self, client, admin, admin_repo, admin_authorization):
        await admin_repo.update(admin, {"is_active": False})
        payload = {"password_1": "testtest", "password_2": "testtest"}
        headers = {"Authorization": admin_authorization}

        response = await client.patch(
            "/admins/change_password", data=dumps(payload), headers=headers
        )
        response_status = response.status_code
        response_json = response.json()
        response_reason = response_json["reason"]

        awaitable_status = 400
        awaitable_reason = "admin_change_password"

        assert response_status == awaitable_status
        assert response_reason == awaitable_reason


@mark.asyncio
class TestProcessLoginView(object):
    async def _register_admin(self, client, mocker, hasher, admin_repo):
        mocker.patch("src.admins.api.admin.messages.SmsService.__call__")
        mocker.patch("src.admins.api.admin.messages.SmsService.as_task")
        mocker.patch("src.admins.api.admin.messages.SmsService.as_future")

        payload = {
            "name": "test",
            "surname": "test",
            "patronymic": "test",
            "phone": "+78005553535",
            "email": "test@gmail.com",
        }

        await client.post("/admins/register", data=dumps(payload))

        admin = await admin_repo.retrieve({"email": "test@gmail.com"})

        admin = await admin_repo.update(
            admin, {"one_time_password": None, "password": hasher.hash("testtest")}
        )
        return admin

    async def test_success(
        self,
        client,
        mocker,
        hasher,
        agency,
        admin_repo,
        agency_repo,
        agent_repo,
        repres_repo,
        user_repo,
        repres_factory,
        user_factory,
    ):
        repres = await repres_factory(email="test@gmail.com")
        user = await user_factory(email="test@gmail.com")
        await repres_repo.update(repres, {"is_active": True})
        await user_repo.update(user, {"is_active": True})

        admin = await self._register_admin(client, mocker, hasher, admin_repo)
        await admin_repo.update(admin, {"is_active": True})
        mocker.patch("src.admins.use_cases.ProcessLoginCase._remove_change_password_permission")

        payload = {"email": admin.email.upper(), "password": "testtest"}

        response = await client.post("/admins/login", data=dumps(payload))
        response_status = response.status_code

        awaitable_status = 200

        assert response_status == awaitable_status

    async def test_fail(
        self,
        client,
        mocker,
        hasher,
        agency,
        admin_repo,
        agency_repo,
        agent_repo,
        repres_repo,
        user_repo,
        repres_factory,
        user_factory,
    ):
        repres = await repres_factory(email="test@gmail.com")
        user = await user_factory(email="test@gmail.com")
        await repres_repo.update(repres, {"is_active": True})
        await user_repo.update(user, {"is_active": True})

        admin = await self._register_admin(client, mocker, hasher, admin_repo)
        await admin_repo.update(admin, {"is_active": True})
        mocker.patch("src.admins.use_cases.ProcessLoginCase._remove_change_password_permission")

        payload = {"email": admin.email, "password": "testtest1"}

        response = await client.post("/admins/login", data=dumps(payload))
        response_status = response.status_code
        response_json = response.json()
        response_reason = response_json["reason"]

        awaitable_status = 400
        awaitable_reason = "admin_wrong_password"

        assert response_status == awaitable_status
        assert response_reason == awaitable_reason

    async def test_not_found(self, client, repres_factory, user_factory, repres_repo, user_repo):
        repres = await repres_factory(email="test@gmail.com")
        user = await user_factory(email="test@gmail.com")
        await repres_repo.update(repres, {"is_active": True})
        await user_repo.update(user, {"is_active": True})

        payload = {"email": "wrong@gmail.com", "password": "testtest1"}

        response = await client.post("/admins/login", data=dumps(payload))
        response_status = response.status_code
        response_json = response.json()
        response_reason = response_json["reason"]

        awaitable_status = 404
        awaitable_reason = "admin_not_found"

        assert response_status == awaitable_status
        assert response_reason == awaitable_reason

    async def test_one_time_success(self, client, mocker, hasher, admin_repo):
        admin = await self._register_admin(client, mocker, hasher, admin_repo)
        mocker.patch("src.admins.use_cases.ProcessLoginCase._remove_change_password_permission")
        await admin_repo.update(admin, {"one_time_password": hasher.hash("testtesttest")})

        payload = {"email": admin.email.upper(), "password": "testtesttest"}
        response = await client.post("/admins/login", data=dumps(payload))
        response_status = response.status_code

        admin = await admin_repo.retrieve({"id": admin.id})

        awaitable_status = 200

        assert admin.reset_time is not None
        assert response_status == awaitable_status

    async def test_one_time_fail(self, client, mocker, hasher, admin_repo):
        admin = await self._register_admin(client, mocker, hasher, admin_repo)
        mocker.patch("src.admins.use_cases.ProcessLoginCase._remove_change_password_permission")
        await admin_repo.update(admin, {"one_time_password": hasher.hash("testtesttest")})

        payload = {"email": admin.email, "password": "testtesttest12"}
        response = await client.post("/admins/login", data=dumps(payload))
        response_status = response.status_code
        response_json = response.json()
        response_reason = response_json["reason"]

        admin = await admin_repo.retrieve({"id": admin.id})

        awaitable_status = 400
        awaitable_reason = "admin_wrong_password"

        assert admin.reset_time is None
        assert response_status == awaitable_status
        assert response_reason == awaitable_reason


@mark.asyncio
class TestSetPasswordView(object):
    async def test_success(
        self,
        client_with_session_cookie: httpx.AsyncClient,
        admin,
        mocker,
        admin_repo,
        create_email_token,
    ):
        # email_reset
        mocker.patch("src.admins.use_cases.EmailResetCase._send_email")
        mocker.patch("src.admins.use_cases.ResetPasswordCase._remove_discard")
        mocker.patch("src.admins.use_cases.SetPasswordCase._send_email")
        payload = {"email": admin.email.upper()}

        response = await client_with_session_cookie.post("/admins/email_reset", data=dumps(payload))
        response_status = response.status_code

        admin = await admin_repo.retrieve({"id": admin.id})

        awaitable_status = 204

        assert admin.discard_token is not None
        assert response_status == awaitable_status

        # reset_password
        response = await client_with_session_cookie.get(
            "/admins/reset_password?q={}&p={}".format(
                create_email_token(admin.id), admin.discard_token
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
            "/admins/set_password", data=dumps(payload)
        )
        assert response.status_code == 200
