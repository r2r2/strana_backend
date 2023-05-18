from pytz import UTC
from json import dumps
from uuid import uuid4
from pytest import mark
from secrets import token_urlsafe
from datetime import datetime, timedelta


@mark.asyncio
class TestSendCodeView(object):
    async def test_success(self, client, mocker, user_repo):
        mocker.patch("src.users.api.user.messages.SmsService.__call__")
        mocker.patch("src.users.api.user.messages.SmsService.as_task")
        mocker.patch("src.users.api.user.messages.SmsService.as_future")

        payload = {"phone": "+79296010017"}

        response = await client.post("/users/send_code", data=dumps(payload))
        response_status = response.status_code

        awaitable_status = 200

        assert response_status == awaitable_status

        user = await user_repo.retrieve(payload)

        assert user is not None
        assert user.token is not None
        assert user.password is not None
        assert user.code_time is not None
        assert user.phone == payload["phone"]

    async def test_existing(self, client, user, mocker, user_repo):
        mocker.patch("src.users.api.user.messages.SmsService.__call__")
        mocker.patch("src.users.api.user.messages.SmsService.as_task")
        mocker.patch("src.users.api.user.messages.SmsService.as_future")

        payload = {"phone": "+79296010017"}

        response = await client.post("/users/send_code", data=dumps(payload))
        response_status = response.status_code

        awaitable_status = 200

        assert response_status == awaitable_status

        updated_user = await user_repo.retrieve(payload)

        token_1 = user.token
        password_1 = user.password
        code_time_1 = user.code_time

        token_2 = updated_user.token
        password_2 = updated_user.password
        code_time_2 = updated_user.code_time

        assert token_1 != token_2
        assert password_1 != password_2
        assert code_time_1 != code_time_2


@mark.asyncio
class TestValidateCodeView(object):
    async def test_success(self, client, user, mocker, user_repo):
        mocker.patch("src.users.api.user.services.CreateContactService.__call__")

        payload = {"phone": str(user.phone), "token": str(user.token), "code": str(user.code)}

        assert not user.is_active
        assert user.is_independent_client is False

        response = await client.post("/users/validate_code", data=dumps(payload))
        response_status = response.status_code
        response_json = response.json()

        awaitable_status = 200

        assert response_status == awaitable_status
        assert "type" in response_json
        assert "token" in response_json
        await user.refresh_from_db()
        assert user.is_independent_client is True

    async def test_not_found(self, client, user, mocker):
        mocker.patch("src.users.api.user.services.CreateContactService.__call__")

        payload = {"phone": "+78005553535", "token": str(user.token), "code": str(user.code)}

        response = await client.post("users/validate_code", data=dumps(payload))
        response_status = response.status_code
        response_json = response.json()
        response_reason = response_json["reason"]

        awaitable_status = 404
        awaitable_reason = "user_not_found"

        assert response_status == awaitable_status
        assert response_reason == awaitable_reason

    async def test_wrong_code(self, client, user, mocker):
        mocker.patch("src.users.api.user.services.CreateContactService.__call__")

        payload = {"phone": str(user.phone), "token": str(user.token), "code": "test"}

        response = await client.post("/users/validate_code", data=dumps(payload))
        response_status = response.status_code
        response_json = response.json()
        response_reason = response_json["reason"]

        awaitable_status = 400
        awaitable_reason = "wrong_code"

        assert response_status == awaitable_status
        assert response_reason == awaitable_reason

    async def test_wrong_token(self, client, user, mocker):
        mocker.patch("src.users.api.user.services.CreateContactService.__call__")

        payload = {"phone": str(user.phone), "token": str(uuid4()), "code": str(user.code)}

        response = await client.post("/users/validate_code", data=dumps(payload))
        response_status = response.status_code
        response_json = response.json()
        response_reason = response_json["reason"]

        awaitable_status = 400
        awaitable_reason = "wrong_code"

        assert response_status == awaitable_status
        assert response_reason == awaitable_reason

    async def test_code_timeout(self, client, user, mocker, user_repo):
        update_data = {"code_time": datetime.now(tz=UTC) - timedelta(minutes=10)}
        await user_repo.update(user, update_data)

        mocker.patch("src.users.api.user.services.CreateContactService.__call__")

        user = await user_repo.retrieve({"id": user.id})

        payload = {"phone": str(user.phone), "token": str(user.token), "code": str(user.code)}

        response = await client.post("/users/validate_code", data=dumps(payload))
        response_status = response.status_code
        response_json = response.json()
        response_reason = response_json["reason"]

        awaitable_status = 400
        awaitable_reason = "user_code_timeout"

        assert response_status == awaitable_status
        assert response_reason == awaitable_reason


@mark.asyncio
class TestUpdatePersonalView(object):
    async def test_unauthorized(self, client, mocker):
        mocker.patch("src.users.api.user.use_cases.UpdatePersonalCase._send_email")
        mocker.patch("src.users.api.user.email.EmailService.__call__")
        mocker.patch("src.users.api.user.email.EmailService.as_task")
        mocker.patch("src.users.api.user.email.EmailService.as_future")
        mocker.patch("src.users.api.user.use_cases.UpdatePersonalCase._amocrm_update")

        response = await client.patch("/users/update_personal")
        response_status = response.status_code

        awaitable_status = 401

        assert response_status == awaitable_status

    async def test_validation(self, client, mocker, user_authorization):
        mocker.patch("src.users.api.user.use_cases.UpdatePersonalCase._send_email")
        mocker.patch("src.users.api.user.email.EmailService.__call__")
        mocker.patch("src.users.api.user.email.EmailService.as_task")
        mocker.patch("src.users.api.user.email.EmailService.as_future")
        mocker.patch("src.users.api.user.use_cases.UpdatePersonalCase._amocrm_update")

        headers = {"Authorization": user_authorization}

        response = await client.patch("/users/update_personal", headers=headers)
        response_status = response.status_code

        awaitable_status = 422

        assert response_status == awaitable_status

    async def test_success(self, client, mocker, user_authorization):
        mocker.patch("src.users.api.user.use_cases.UpdatePersonalCase._send_email")
        mocker.patch("src.users.api.user.email.EmailService.__call__")
        mocker.patch("src.users.api.user.email.EmailService.as_task")
        mocker.patch("src.users.api.user.email.EmailService.as_future")
        mocker.patch("src.users.api.user.use_cases.UpdatePersonalCase._amocrm_update")

        headers = {"Authorization": user_authorization}

        payload = {
            "email": "new@gmail.com",
            "name": "new",
            "surname": "new",
            "patronymic": "new",
            "birth_date": "2000-08-21",
            "passport_series": "0987",
            "passport_number": "555555",
        }

        response = await client.patch(
            "/users/update_personal", headers=headers, data=dumps(payload)
        )
        response_status = response.status_code

        awaitable_status = 200

        assert response_status == awaitable_status

    async def test_not_found(self, client, mocker, fake_user_authorization):
        mocker.patch("src.users.api.user.use_cases.UpdatePersonalCase._send_email")
        mocker.patch("src.users.api.user.email.EmailService.__call__")
        mocker.patch("src.users.api.user.email.EmailService.as_task")
        mocker.patch("src.users.api.user.email.EmailService.as_future")
        mocker.patch("src.users.api.user.use_cases.UpdatePersonalCase._amocrm_update")

        fake_headers = {"Authorization": fake_user_authorization}

        payload = {
            "email": "new@gmail.com",
            "name": "new",
            "surname": "new",
            "patronymic": "new",
            "birth_date": "2000-08-21",
            "passport_series": "0987",
            "passport_number": "555555",
        }

        response = await client.patch(
            "/users/update_personal", headers=fake_headers, data=dumps(payload)
        )
        response_status = response.status_code

        awaitable_status = 403

        assert response_status == awaitable_status


@mark.asyncio
class TestGetMeView(object):
    async def test_unauthorized(self, client):

        response = await client.get("/users/me")
        response_status = response.status_code

        awaitable_status = 401

        assert response_status == awaitable_status

    async def test_success(self, client, user_authorization):
        headers = {"Authorization": user_authorization}

        response = await client.get("/users/me", headers=headers)
        response_status = response.status_code

        awaitable_status = 200

        assert response_status == awaitable_status

    async def test_not_found(self, client, fake_user_authorization):
        fake_headers = {"Authorization": fake_user_authorization}

        response = await client.get("/users/me", headers=fake_headers)
        response_status = response.status_code

        awaitable_status = 403

        assert response_status == awaitable_status


@mark.asyncio
class TestSessionTokenView(object):
    async def test_success(self, client):
        response = await client.get("/users/session_token")
        response_status = response.status_code
        response_json = response.json()

        awaitable_status = 200
        awaitable_type_name = "type"
        awaitable_token_name = "token"

        assert response_status == awaitable_status
        assert awaitable_type_name in response_json
        assert awaitable_token_name in response_json


@mark.asyncio
class TestChangePhoneView(object):
    async def test_success(self, client, user, mocker, user_repo, user_authorization):
        mocker.patch("src.users.api.user.use_cases.ChangePhoneCase._amocrm_update")

        payload = {"phone": "+79025664312", "code": str(user.code), "token": str(user.token)}
        headers = {"Authorization": user_authorization}

        await user_repo.update_or_create(
            {"phone": "+79025664312"},
            {
                "is_imported": False,
                "code": str(user.code),
                "token": str(user.token),
                "code_time": user.code_time,
            },
        )

        response = await client.patch("/users/change_phone", data=dumps(payload), headers=headers)
        response_status = response.status_code

        awaitable_status = 200
        awaitable_users_len = 1
        awaitable_phone = "+79025664312"

        user = await user_repo.retrieve({"id": user.id})
        users = await user_repo.list({})

        assert user.phone == awaitable_phone
        assert len(users) == awaitable_users_len
        assert response_status == awaitable_status

    async def test_phone_taken(self, client, user, user_repo, mocker, user_authorization):
        mocker.patch("src.users.api.user.use_cases.ChangePhoneCase._amocrm_update")

        payload = {"phone": "+79025664312", "code": str(user.code), "token": str(user.token)}
        headers = {"Authorization": user_authorization}

        await user_repo.update_or_create({"phone": "+79025664312"}, {"is_imported": True})

        response = await client.patch("/users/change_phone", data=dumps(payload), headers=headers)
        response_status = response.status_code
        response_json = response.json()
        response_reason = response_json["reason"]

        awaitable_status = 400
        awaitable_reason = "user_phone_taken"

        assert response_status == awaitable_status
        assert response_reason == awaitable_reason

    async def test_code_invalid(self, client, user, mocker, user_repo, user_authorization):
        mocker.patch("src.users.api.user.use_cases.ChangePhoneCase._amocrm_update")

        payload = {"phone": "+79025664312", "code": "fdgfdgffff", "token": str(user.token)}
        headers = {"Authorization": user_authorization}

        await user_repo.update_or_create(
            {"phone": "+79025664312"},
            {
                "is_imported": False,
                "code": str(user.code),
                "token": str(user.token),
                "code_time": datetime.now(tz=UTC) + timedelta(minutes=10),
            },
        )

        response = await client.patch("/users/change_phone", data=dumps(payload), headers=headers)
        response_status = response.status_code
        response_json = response.json()
        response_reason = response_json["reason"]

        awaitable_status = 400
        awaitable_reason = "wrong_code"

        assert response_status == awaitable_status
        assert response_reason == awaitable_reason

    async def test_code_timeout(self, client, user, mocker, user_repo, user_authorization):
        mocker.patch("src.users.api.user.use_cases.ChangePhoneCase._amocrm_update")

        update_data = {"code_time": datetime.now(tz=UTC) - timedelta(minutes=10)}
        await user_repo.update(user, update_data)

        await user_repo.update_or_create(
            {"phone": "+79025664312"},
            {
                "is_imported": False,
                "code_time": datetime.now(tz=UTC) - timedelta(minutes=10),
                "token": str(user.token),
                "code": str(user.code),
            },
        )

        payload = {"phone": "+79025664312", "code": str(user.code), "token": str(user.token)}
        headers = {"Authorization": user_authorization}

        response = await client.patch("/users/change_phone", data=dumps(payload), headers=headers)
        response_status = response.status_code
        response_json = response.json()
        response_reason = response_json["reason"]

        awaitable_status = 400
        awaitable_reason = "user_code_timeout"

        assert response_status == awaitable_status
        assert response_reason == awaitable_reason

    async def test_same_phone(self, client, user, mocker, user_repo, user_authorization):
        mocker.patch("src.users.api.user.use_cases.ChangePhoneCase._amocrm_update")

        payload = {"phone": str(user.phone), "code": str(user.code), "token": str(user.token)}
        headers = {"Authorization": user_authorization}

        response = await client.patch("/users/change_phone", data=dumps(payload), headers=headers)
        response_status = response.status_code
        response_json = response.json()
        response_reason = response_json["reason"]

        awaitable_status = 400
        awaitable_reason = "user_phone_same"

        assert response_status == awaitable_status
        assert response_reason == awaitable_reason


@mark.asyncio
class TestConfirmEmailView(object):
    async def test_success(self, client, user, user_repo, create_email_token):
        email_token = token_urlsafe(32)
        update_data = {"is_active": False, "email_token": email_token}
        user = await user_repo.update(user, update_data)
        token = create_email_token(user.id)

        await client.get(f"/users/confirm_email?q={token}&p={email_token}")

        user = await user_repo.retrieve({"id": user.id})

        assert user.is_active
        assert user.email_token is None

    async def test_fail(self, client, user, user_repo, create_email_token):
        email_token = token_urlsafe(32)
        update_data = {"is_active": False, "email_token": token_urlsafe(32)}
        user = await user_repo.update(user, update_data)
        token = create_email_token(user.id)

        await client.get(f"/users/confirm_email?q={token}&p={email_token}")

        user = await user_repo.retrieve({"id": user.id})

        assert not user.is_active
        assert user.email_token is not None


@mark.asyncio
class TestPartialUpdateView(object):
    async def test_success(self, client, mocker, user_authorization):
        mocker.patch("src.users.api.user.use_cases.PartialUpdateCase._send_email")
        mocker.patch("src.users.api.user.email.EmailService.__call__")
        mocker.patch("src.users.api.user.email.EmailService.as_task")
        mocker.patch("src.users.api.user.email.EmailService.as_future")
        mocker.patch("src.users.api.user.use_cases.PartialUpdateCase._amocrm_update")

        headers = {"Authorization": user_authorization}

        payload = {
            "email": "new@gmail.com",
            "name": "new",
            "surname": "new",
            "patronymic": "new",
            "birth_date": "2000-08-21",
        }

        response = await client.patch("/users/partial_update", headers=headers, data=dumps(payload))
        response_status = response.status_code

        awaitable_status = 200

        assert response_status == awaitable_status

    async def test_not_found(self, client, mocker, fake_user_authorization):
        mocker.patch("src.users.api.user.use_cases.UpdatePersonalCase._send_email")
        mocker.patch("src.users.api.user.email.EmailService.__call__")
        mocker.patch("src.users.api.user.email.EmailService.as_task")
        mocker.patch("src.users.api.user.email.EmailService.as_future")
        mocker.patch("src.users.api.user.use_cases.PartialUpdateCase._amocrm_update")

        fake_headers = {"Authorization": fake_user_authorization}

        payload = {
            "email": "new@gmail.com",
            "name": "new",
            "surname": "new",
            "patronymic": "new",
            "birth_date": "2000-08-21",
        }

        response = await client.patch(
            "/users/partial_update", headers=fake_headers, data=dumps(payload)
        )
        response_status = response.status_code

        awaitable_status = 403

        assert response_status == awaitable_status


@mark.asyncio
class TestAgentsUsersListView(object):
    async def test_success(
        self,
        client,
        agent,
        property,
        user_repo,
        user_factory,
        check_factory,
        booking_factory,
        agent_authorization,
    ):
        for _ in range(15):
            user = await user_factory()
            await check_factory(user_id=user.id, agent_id=agent.id)
            for _ in range(4):
                await booking_factory(
                    agent_id=agent.id, user_id=user.id, property=property, decremented=True
                )
            for _ in range(3):
                await booking_factory(
                    agent_id=agent.id, user_id=user.id, property=property, decremented=False
                )
            for _ in range(2):
                await booking_factory(
                    agent_id=agent.id,
                    active=False,
                    user_id=user.id,
                    property=property,
                    decremented=False,
                )
                await booking_factory(user_id=user.id, property=property, decremented=False)
        for _ in range(5):
            user = await user_factory()
            await check_factory(user_id=user.id)

        headers = {"Authorization": agent_authorization}

        response = await client.get("/users/agents", headers=headers)
        response_status = response.status_code
        response_json = response.json()
        response_count = response_json["count"]
        response_info = response_json["page_info"]
        response_booking_count = response_json["result"][0]["booking_count"]
        response_is_decremented = response_json["result"][0]["is_decremented"]

        awaitable_status = 200
        awaitable_count = 15
        awaitable_booking_count = 7
        awaitable_is_decremented = True

        assert response_count == awaitable_count
        assert response_status == awaitable_status
        assert response_info["next_page"] is not None
        assert response_booking_count == awaitable_booking_count
        assert response_is_decremented == awaitable_is_decremented

    async def test_not_authorized(self, client, agent, user_factory, check_factory):
        for _ in range(15):
            user = await user_factory()
            await check_factory(user_id=user.id, agent_id=agent.id)

        response = await client.get("/users/agents")
        response_status = response.status_code

        awaitable_status = 401

        assert response_status == awaitable_status

    async def test_wrong_type(self, client, repres_authorization):
        headers = {"Authorization": repres_authorization}

        response = await client.get("/users/agents", headers=headers)
        response_status = response.status_code

        awaitable_status = 403

        assert response_status == awaitable_status

    async def test_search_filter_success(
        self, client, agent, user_factory, check_factory, agent_authorization
    ):
        for _ in range(15):
            user = await user_factory()
            await check_factory(user_id=user.id, agent_id=agent.id)

        email = user.email

        headers = {"Authorization": agent_authorization}

        response = await client.get(f"/users/agents?search={email}", headers=headers)
        response_status = response.status_code
        response_json = response.json()
        response_count = response_json["count"]
        response_info = response_json["page_info"]

        awaitable_status = 200
        awaitable_count = (0, 1)

        assert response_count in awaitable_count
        assert response_status == awaitable_status
        assert response_info["next_page"] is None

    async def test_search_filter_fail(
        self, client, agent, user_factory, check_factory, agent_authorization
    ):
        for _ in range(15):
            user = await user_factory()
            await check_factory(user_id=user.id, agent_id=agent.id)

        email = user.email

        headers = {"Authorization": agent_authorization}

        response = await client.get(f"/users/agents?search={email}dasdasdas", headers=headers)
        response_status = response.status_code
        response_json = response.json()
        response_count = response_json["count"]
        response_info = response_json["page_info"]

        awaitable_status = 200
        awaitable_count = 0

        assert response_count == awaitable_count
        assert response_status == awaitable_status
        assert response_info["next_page"] is None

    async def test_status_filter_success(
        self,
        client,
        agent,
        property,
        user_factory,
        check_factory,
        booking_factory,
        agent_authorization,
    ):
        for i in range(15):
            user = await user_factory(agent_id=agent.id)
            await check_factory(user_id=user.id, agent_id=agent.id)
            for _ in range(5):
                if i == 5:
                    booking = await booking_factory(
                        user_id=user.id, active=True, property=property, agent_id=agent.id
                    )
                else:
                    booking = await booking_factory(
                        user_id=user.id, active=False, property=property, agent_id=agent.id
                    )

        status = booking.amocrm_stage.value

        headers = {"Authorization": agent_authorization}

        response = await client.get(f"/users/agents?status={status}", headers=headers)
        response_status = response.status_code
        response_json = response.json()
        response_count = response_json["count"]
        response_info = response_json["page_info"]

        awaitable_status = 200
        awaitable_count = 1

        assert response_count == awaitable_count
        assert response_status == awaitable_status
        assert response_info["next_page"] is None

    async def test_status_filter_fail(
        self,
        client,
        agent,
        property,
        user_repo,
        user_factory,
        check_factory,
        booking_factory,
        agent_authorization,
    ):
        for i in range(15):
            user = await user_factory()
            await check_factory(user_id=user.id, agent_id=agent.id)
            for _ in range(5):
                if i == 5:
                    booking = await booking_factory(user_id=user.id, active=True, property=property)
                else:
                    booking = await booking_factory(
                        user_id=user.id, active=False, property=property
                    )

        status = booking.amocrm_stage.value

        headers = {"Authorization": agent_authorization}

        response = await client.get(f"/users/agents?status={status}", headers=headers)
        response_status = response.status_code
        response_json = response.json()
        response_count = response_json["count"]
        response_info = response_json["page_info"]

        awaitable_status = 200
        awaitable_count = 0

        assert response_count == awaitable_count
        assert response_status == awaitable_status
        assert response_info["next_page"] is None

    async def test_work_period_filter_success(
        self, client, agent, user_factory, check_factory, agent_authorization
    ):
        for i in range(15):
            user = await user_factory(i=i, agent_id=agent.id)
            await check_factory(user_id=user.id, agent_id=agent.id)

        work_period = f"{user.work_start.isoformat()}__{user.work_end.isoformat()}"

        headers = {"Authorization": agent_authorization}

        response = await client.get(f"/users/agents?work_period={work_period}", headers=headers)
        response_status = response.status_code
        response_json = response.json()
        response_count = response_json["count"]
        response_info = response_json["page_info"]

        awaitable_status = 200
        awaitable_count = 1

        assert response_count == awaitable_count
        assert response_status == awaitable_status
        assert response_info["next_page"] is None

    async def test_work_period_filter_fail(
        self, client, agent, user_factory, check_factory, agent_authorization
    ):
        for i in range(15):
            user = await user_factory(i=i)
            await check_factory(user_id=user.id, agent_id=agent.id)

        work_period = f"{user.work_start.isoformat()}__dasdas{user.work_end.isoformat()}"

        headers = {"Authorization": agent_authorization}

        response = await client.get(f"/users/agents?work_period={work_period}", headers=headers)
        response_status = response.status_code
        response_json = response.json()

        response_count = response_json["count"]
        response_info = response_json["page_info"]

        awaitable_status = 200
        awaitable_count = 15

        assert response_count == awaitable_count
        assert response_status == awaitable_status
        assert response_info["next_page"] is not None

    async def test_property_type_filter_success(
        self,
        client,
        agent,
        property,
        user_factory,
        check_factory,
        booking_factory,
        agent_authorization,
    ):
        for i in range(15):
            user = await user_factory(agent_id=agent.id)
            await check_factory(user_id=user.id, agent_id=agent.id)
            for __ in range(5):
                if i == 5:
                    await booking_factory(
                        user_id=user.id, active=True, property=property, agent_id=agent.id
                    )
                else:
                    await booking_factory(
                        user_id=user.id, active=False, property=property, agent_id=agent.id
                    )

        property_type = property.type.value

        headers = {"Authorization": agent_authorization}

        response = await client.get(f"/users/agents?property_type={property_type}", headers=headers)
        response_status = response.status_code
        response_json = response.json()
        response_count = response_json["count"]
        response_info = response_json["page_info"]

        awaitable_status = 200
        awaitable_count = 1

        assert response_count == awaitable_count
        assert response_status == awaitable_status
        assert response_info["next_page"] is None

    async def test_property_type_filter_fail(
        self,
        client,
        agent,
        property,
        user_factory,
        check_factory,
        booking_factory,
        agent_authorization,
    ):
        for i in range(15):
            user = await user_factory()
            await check_factory(user_id=user.id, agent_id=agent.id)
            for __ in range(5):
                if i == 5:
                    await booking_factory(user_id=user.id, active=True, property=property)
                else:
                    await booking_factory(user_id=user.id, active=False, property=property)

        property_type = property.type.value

        headers = {"Authorization": agent_authorization}

        response = await client.get(f"/users/agents?property_type={property_type}", headers=headers)
        response_status = response.status_code
        response_json = response.json()
        response_count = response_json["count"]
        response_info = response_json["page_info"]

        awaitable_status = 200
        awaitable_count = 0

        assert response_count == awaitable_count
        assert response_status == awaitable_status
        assert response_info["next_page"] is None

    async def test_project_filter_success(
        self,
        client,
        agent,
        property,
        user_factory,
        check_factory,
        booking_factory,
        agent_authorization,
    ):
        for i in range(15):
            user = await user_factory(agent_id=agent.id)
            await check_factory(user_id=user.id, agent_id=agent.id)
            for __ in range(5):
                if i == 5:
                    await booking_factory(
                        user_id=user.id, active=True, property=property, agent_id=agent.id
                    )
                else:
                    await booking_factory(
                        user_id=user.id, active=False, property=property, agent_id=agent.id
                    )

        project = property.project.slug

        headers = {"Authorization": agent_authorization}

        response = await client.get(f"/users/agents?project={project}", headers=headers)
        response_status = response.status_code
        response_json = response.json()
        response_count = response_json["count"]
        response_info = response_json["page_info"]

        awaitable_status = 200
        awaitable_count = 1

        assert response_count == awaitable_count
        assert response_status == awaitable_status
        assert response_info["next_page"] is None

    async def test_project_filter_fail(
        self,
        client,
        agent,
        property,
        user_factory,
        check_factory,
        booking_factory,
        agent_authorization,
    ):
        for i in range(15):
            user = await user_factory()
            await check_factory(user_id=user.id, agent_id=agent.id)
            for __ in range(5):
                if i == 5:
                    await booking_factory(user_id=user.id, active=True, property=property)
                else:
                    await booking_factory(user_id=user.id, active=False, property=property)

        project = property.project.slug

        headers = {"Authorization": agent_authorization}

        response = await client.get(f"/users/agents?project={project}", headers=headers)
        response_status = response.status_code
        response_json = response.json()
        response_count = response_json["count"]
        response_info = response_json["page_info"]

        awaitable_status = 200
        awaitable_count = 0

        assert response_count == awaitable_count
        assert response_status == awaitable_status
        assert response_info["next_page"] is None


@mark.asyncio
class TestAgentsUsersRetrieveView(object):
    async def test_success_main(
        self,
        client,
        agent,
        booking,
        property,
        user_repo,
        booking_repo,
        user_factory,
        check_factory,
        property_factory,
        agent_authorization,
        property_repo,
    ):
        await property_repo.update(property, {"plan": "test", "plan_png": "test"})
        user = await user_factory(agent_id=agent.id)
        await check_factory(agent_id=agent.id, user_id=user.id)
        await booking_repo.update(booking, {"user_id": user.id, "agent_id": agent.id})
        await user_repo.add_m2m(user, "interested", [property])

        headers = {"Authorization": agent_authorization}

        response = await client.get(f"/users/agents/{user.id}", headers=headers)
        response_status = response.status_code
        response_json = response.json()
        response_indents = response_json["indents"]
        response_interested = response_json["interesting"]
        response_stat = response_json["status"]["value"]

        awaitable_status = 200
        awaitable_stat = "check"

        assert response_indents
        assert response_interested
        assert response_stat == awaitable_stat
        assert response_status == awaitable_status

    async def test_success_other(
        self,
        client,
        agent,
        booking,
        user_repo,
        booking_repo,
        user_factory,
        check_factory,
        property_factory,
        agent_authorization,
    ):
        user = await user_factory()
        check = await check_factory(agent_id=agent.id, user_id=user.id)
        await user_repo.add_m2m(user, "checkers", [check])
        await booking_repo.update(booking, {"user_id": user.id})

        headers = {"Authorization": agent_authorization}

        response = await client.get(f"/users/agents/{user.id}", headers=headers)
        response_status = response.status_code
        response_json = response.json()
        response_indents = response_json["indents"]
        response_interested = response_json["interesting"]
        response_stat = response_json["status"]["value"]

        awaitable_status = 200
        awaitable_stat = "check"

        assert response_indents is None
        assert response_interested is None
        assert response_stat == awaitable_stat
        assert response_status == awaitable_status

    async def test_fail(self, client, agent, user_factory, agent_authorization):
        user = await user_factory(agent_id=agent.id)

        headers = {"Authorization": agent_authorization}

        response = await client.get(f"/users/agents/{user.id}", headers=headers)
        response_status = response.status_code
        response_json = response.json()
        response_reason = response_json["reason"]

        awaitable_status = 404
        awaitable_reason = "user_not_found"

        assert response_status == awaitable_status
        assert response_reason == awaitable_reason


@mark.asyncio
class TestAgentsUsersSpecsView(object):
    async def test_success(
        self,
        client,
        agent,
        user_factory,
        floor_factory,
        booking_factory,
        project_factory,
        property_factory,
        building_factory,
        agent_authorization,
    ):
        c = 0
        for i in range(3):
            project = await project_factory(i=i)
            for j in range(5):
                building = await building_factory(project_id=project.id, i=c)
                floor = await floor_factory(project_id=project.id, building_id=building.id, i=c)
                if j != 2:
                    property = await property_factory(
                        project_id=project.id, building_id=building.id, floor_id=floor.id, i=c
                    )
                else:
                    property = await property_factory(
                        project_id=project.id,
                        building_id=building.id,
                        floor_id=floor.id,
                        type="COMMERCIAL",
                        i=c,
                    )
                user = await user_factory(agent_id=agent.id, i=c)
                if j != 2:
                    await booking_factory(
                        property=property,
                        building=building,
                        user_id=user.id,
                        i=c,
                        agent_id=agent.id,
                    )
                elif j == 3:
                    await booking_factory(
                        property=property,
                        building=building,
                        user_id=user.id,
                        amocrm_stage="ddu_unregistered",
                        i=c,
                        active=False,
                        agent_id=agent.id,
                    )
                else:
                    await booking_factory(
                        property=property,
                        building=building,
                        user_id=user.id,
                        amocrm_stage="booking",
                        i=c,
                        agent_id=agent.id,
                    )
                c += 1

        headers = {"Authorization": agent_authorization}

        response = await client.get("/users/agents/specs", headers=headers)
        response_status = response.status_code
        response_json = response.json()
        response_ordering = response_json["ordering"]
        response_specs = response_json["specs"]

        awaitable_status = 200
        awaitable_specs_len = 5
        awaitable_ordering_len = 4

        assert response_specs.get("agent")
        assert response_specs.get("status")
        assert response_specs.get("project")
        assert response_specs.get("work_period")
        assert response_specs.get("property_type")
        assert response_status == awaitable_status
        assert len(response_specs) == awaitable_specs_len
        assert len(response_ordering) == awaitable_ordering_len

    async def test_fail(
        self,
        client,
        agent,
        user_factory,
        floor_factory,
        booking_factory,
        project_factory,
        property_factory,
        building_factory,
        agent_authorization,
    ):
        c = 0
        for i in range(3):
            project = await project_factory(i=i)
            for j in range(5):
                building = await building_factory(project_id=project.id, i=c)
                floor = await floor_factory(project_id=project.id, building_id=building.id, i=c)
                if j != 2:
                    property = await property_factory(
                        project_id=project.id, building_id=building.id, floor_id=floor.id, i=c
                    )
                else:
                    property = await property_factory(
                        project_id=project.id,
                        building_id=building.id,
                        floor_id=floor.id,
                        type="COMMERCIAL",
                        i=c,
                    )
                user = await user_factory(agent_id=None, i=c)
                if j != 2:
                    await booking_factory(
                        property=property, building=building, user_id=user.id, i=c
                    )
                elif j == 3:
                    await booking_factory(
                        property=property,
                        building=building,
                        user_id=user.id,
                        amocrm_stage="ddu_unregistered",
                        i=c,
                        active=False,
                    )
                else:
                    await booking_factory(
                        property=property,
                        building=building,
                        user_id=user.id,
                        amocrm_stage="booking",
                        i=c,
                    )
                c += 1

        headers = {"Authorization": agent_authorization}

        response = await client.get("/users/agents/specs", headers=headers)
        response_status = response.status_code
        response_json = response.json()
        response_ordering = response_json["ordering"]
        response_specs = response_json["specs"]

        awaitable_status = 200
        awaitable_specs_len = 5
        awaitable_ordering_len = 4

        assert not response_specs.get("agent")
        assert not response_specs.get("status")
        assert not response_specs.get("project")
        assert response_status == awaitable_status
        assert not response_specs.get("work_period")
        assert not response_specs.get("property_type")
        assert len(response_specs) == awaitable_specs_len
        assert len(response_ordering) == awaitable_ordering_len


@mark.asyncio
class TestAgentsUsersFacetsView(object):
    async def test_success(
        self,
        client,
        agent,
        user_factory,
        floor_factory,
        booking_factory,
        project_factory,
        property_factory,
        building_factory,
        agent_authorization,
    ):
        c = 0
        for i in range(3):
            project = await project_factory(i=i)
            for j in range(5):
                building = await building_factory(project_id=project.id, i=c)
                floor = await floor_factory(project_id=project.id, building_id=building.id, i=c)
                if j != 2:
                    property = await property_factory(
                        project_id=project.id, building_id=building.id, floor_id=floor.id, i=c
                    )
                else:
                    property = await property_factory(
                        project_id=project.id,
                        building_id=building.id,
                        floor_id=floor.id,
                        type="COMMERCIAL",
                        i=c,
                    )
                user = await user_factory(agent_id=agent.id, i=c)
                if j != 2:
                    await booking_factory(
                        property=property,
                        building=building,
                        user_id=user.id,
                        i=c,
                        agent_id=agent.id,
                    )
                elif j == 3:
                    await booking_factory(
                        property=property,
                        building=building,
                        user_id=user.id,
                        amocrm_stage="ddu_unregistered",
                        i=c,
                        active=False,
                        agent_id=agent.id,
                    )
                else:
                    await booking_factory(
                        property=property,
                        building=building,
                        user_id=user.id,
                        amocrm_stage="booking",
                        i=c,
                        agent_id=agent.id,
                    )
                c += 1

        headers = {"Authorization": agent_authorization}

        response = await client.get("/users/agents/facets", headers=headers)
        response_status = response.status_code
        response_json = response.json()
        response_count = response_json["count"]
        response_facets = response_json["facets"]

        awaitable_count = 15
        awaitable_status = 200
        awaitable_facets_len = 5

        assert response_facets.get("agent")
        assert response_facets.get("status")
        assert response_facets.get("project")
        assert response_count == awaitable_count
        assert response_facets.get("work_period")
        assert response_facets.get("property_type")
        assert response_status == awaitable_status
        assert len(response_facets) == awaitable_facets_len

    async def test_success_filtered(
        self,
        client,
        agent,
        user_factory,
        floor_factory,
        booking_factory,
        project_factory,
        property_factory,
        building_factory,
        agent_authorization,
    ):
        c = 0
        for i in range(3):
            project = await project_factory(i=i)
            for j in range(5):
                building = await building_factory(project_id=project.id, i=c)
                floor = await floor_factory(project_id=project.id, building_id=building.id, i=c)
                if j != 2:
                    property = await property_factory(
                        project_id=project.id, building_id=building.id, floor_id=floor.id, i=c
                    )
                else:
                    property = await property_factory(
                        project_id=project.id,
                        building_id=building.id,
                        floor_id=floor.id,
                        type="COMMERCIAL",
                        i=c,
                    )
                user = await user_factory(agent_id=agent.id, i=c)
                if j != 2:
                    await booking_factory(
                        property=property,
                        building=building,
                        user_id=user.id,
                        i=c,
                        agent_id=agent.id,
                    )
                elif j == 3:
                    await booking_factory(
                        property=property,
                        building=building,
                        user_id=user.id,
                        amocrm_stage="ddu_unregistered",
                        i=c,
                        active=False,
                        agent_id=agent.id,
                    )
                else:
                    await booking_factory(
                        property=property,
                        building=building,
                        user_id=user.id,
                        amocrm_stage="booking",
                        i=c,
                        agent_id=agent.id,
                    )
                c += 1

        headers = {"Authorization": agent_authorization}

        response = await client.get(f"/users/agents/facets?project={project.slug}", headers=headers)
        response_status = response.status_code
        response_json = response.json()
        response_count = response_json["count"]
        response_facets = response_json["facets"]

        awaitable_count = 5
        awaitable_status = 200
        awaitable_facets_len = 5

        assert response_facets.get("agent")
        assert response_facets.get("status")
        assert response_facets.get("project")
        assert response_count == awaitable_count
        assert response_facets.get("work_period")
        assert response_facets.get("property_type")
        assert response_status == awaitable_status
        assert len(response_facets) == awaitable_facets_len

    async def test_fail(
        self,
        client,
        agent,
        user_factory,
        floor_factory,
        booking_factory,
        project_factory,
        property_factory,
        building_factory,
        agent_authorization,
    ):
        c = 0
        for i in range(3):
            project = await project_factory(i=i)
            for j in range(5):
                building = await building_factory(project_id=project.id, i=c)
                floor = await floor_factory(project_id=project.id, building_id=building.id, i=c)
                if j != 2:
                    property = await property_factory(
                        project_id=project.id, building_id=building.id, floor_id=floor.id, i=c
                    )
                else:
                    property = await property_factory(
                        project_id=project.id,
                        building_id=building.id,
                        floor_id=floor.id,
                        type="COMMERCIAL",
                        i=c,
                    )
                user = await user_factory(agent_id=None, i=c)
                if j != 2:
                    await booking_factory(
                        property=property, building=building, user_id=user.id, i=c
                    )
                elif j == 3:
                    await booking_factory(
                        property=property,
                        building=building,
                        user_id=user.id,
                        amocrm_stage="ddu_unregistered",
                        i=c,
                        active=False,
                    )
                else:
                    await booking_factory(
                        property=property,
                        building=building,
                        user_id=user.id,
                        amocrm_stage="booking",
                        i=c,
                    )
                c += 1

        headers = {"Authorization": agent_authorization}

        response = await client.get(f"/users/agents/facets?project={project.slug}", headers=headers)
        response_status = response.status_code
        response_json = response.json()
        response_count = response_json["count"]
        response_facets = response_json["facets"]

        awaitable_count = 0
        awaitable_status = 200
        awaitable_facets_len = 5

        assert not response_facets.get("agent")
        assert not response_facets.get("status")
        assert not response_facets.get("project")
        assert response_count == awaitable_count
        assert response_status == awaitable_status
        assert not response_facets.get("work_period")
        assert not response_facets.get("property_type")
        assert len(response_facets) == awaitable_facets_len


@mark.asyncio
class TestAgentsUsersInterestView(object):
    async def test_success(
        self,
        client,
        agent,
        user_repo,
        user_factory,
        floor_factory,
        project_factory,
        building_factory,
        property_factory,
        agent_authorization,
    ):
        c = 0
        properties = []
        for i in range(3):
            project = await project_factory(i=i)
            for j in range(5):
                building = await building_factory(project_id=project.id, i=c)
                floor = await floor_factory(project_id=project.id, building_id=building.id, i=c)
                if j != 2:
                    property = await property_factory(
                        project_id=project.id, building_id=building.id, floor_id=floor.id, i=c
                    )
                else:
                    property = await property_factory(
                        project_id=project.id,
                        building_id=building.id,
                        floor_id=floor.id,
                        type="COMMERCIAL",
                        i=c,
                    )
                properties.append(property)
                user = await user_factory(agent_id=agent.id, i=c)
                c += 1

        user = await user_repo.retrieve({"id": user.id}, prefetch_fields=["interested"])

        awaitable_interested_len = 0

        assert len(user.interested) == awaitable_interested_len

        headers = {"Authorization": agent_authorization}
        payload = {
            "interested_type": "FLAT",
            "interested_project": project.id,
            "interested": [prop.id for prop in properties[:3]],
        }

        response = await client.patch(
            f"/users/agents/interest/{user.id}", headers=headers, data=dumps(payload)
        )
        response_status = response.status_code

        user = await user_repo.retrieve({"id": user.id}, prefetch_fields=["interested"])

        awaitable_status = 200
        awaitable_interested_len = 3
        awaitable_interested_type = "FLAT"
        awaitable_interested_project = project.id

        assert response_status == awaitable_status
        assert len(user.interested) == awaitable_interested_len
        assert user.interested_type == awaitable_interested_type
        assert user.interested_project_id == awaitable_interested_project

    async def test_no_duplicates(
        self,
        client,
        agent,
        user_repo,
        user_factory,
        floor_factory,
        project_factory,
        building_factory,
        property_factory,
        agent_authorization,
    ):
        c = 0
        properties = []
        for i in range(3):
            project = await project_factory(i=i)
            for j in range(5):
                building = await building_factory(project_id=project.id, i=c)
                floor = await floor_factory(project_id=project.id, building_id=building.id, i=c)
                if j != 2:
                    property = await property_factory(
                        project_id=project.id, building_id=building.id, floor_id=floor.id, i=c
                    )
                else:
                    property = await property_factory(
                        project_id=project.id,
                        building_id=building.id,
                        floor_id=floor.id,
                        type="COMMERCIAL",
                        i=c,
                    )
                properties.append(property)
                user = await user_factory(agent_id=agent.id, i=c)
                c += 1

        user = await user_repo.retrieve({"id": user.id}, prefetch_fields=["interested"])

        awaitable_interested_len = 0

        assert len(user.interested) == awaitable_interested_len

        headers = {"Authorization": agent_authorization}
        payload = {
            "interested_type": "FLAT",
            "interested_project": project.id,
            "interested": [prop.id for prop in properties[:3]],
        }

        response = await client.patch(
            f"/users/agents/interest/{user.id}", headers=headers, data=dumps(payload)
        )
        response_status = response.status_code

        user = await user_repo.retrieve({"id": user.id}, prefetch_fields=["interested"])

        awaitable_status = 200
        awaitable_interested_len = 3
        awaitable_interested_type = "FLAT"
        awaitable_interested_project = project.id

        assert response_status == awaitable_status
        assert len(user.interested) == awaitable_interested_len
        assert user.interested_type == awaitable_interested_type
        assert user.interested_project_id == awaitable_interested_project

        response = await client.patch(
            f"/users/agents/interest/{user.id}", headers=headers, data=dumps(payload)
        )
        response_status = response.status_code

        user = await user_repo.retrieve({"id": user.id}, prefetch_fields=["interested"])

        awaitable_status = 200
        awaitable_interested_len = 3
        awaitable_interested_type = "FLAT"
        awaitable_interested_project = project.id

        assert response_status == awaitable_status
        assert len(user.interested) == awaitable_interested_len
        assert user.interested_type == awaitable_interested_type
        assert user.interested_project_id == awaitable_interested_project

    async def test_not_found(
        self,
        client,
        agent,
        user_repo,
        user_factory,
        floor_factory,
        project_factory,
        building_factory,
        property_factory,
        agent_authorization,
    ):
        c = 0
        properties = []
        for i in range(3):
            project = await project_factory(i=i)
            for j in range(5):
                building = await building_factory(project_id=project.id, i=c)
                floor = await floor_factory(project_id=project.id, building_id=building.id, i=c)
                if j != 2:
                    property = await property_factory(
                        project_id=project.id, building_id=building.id, floor_id=floor.id, i=c
                    )
                else:
                    property = await property_factory(
                        project_id=project.id,
                        building_id=building.id,
                        floor_id=floor.id,
                        type="COMMERCIAL",
                        i=c,
                    )
                properties.append(property)
                user = await user_factory(i=c)
                c += 1

        headers = {"Authorization": agent_authorization}
        payload = {
            "interested_type": "FLAT",
            "interested_project": project.id,
            "interested": [prop.id for prop in properties[:3]],
        }

        response = await client.patch(
            f"/users/agents/interest/{user.id}", headers=headers, data=dumps(payload)
        )
        response_status = response.status_code
        response_json = response.json()
        response_reason = response_json["reason"]

        awaitable_status = 404
        awaitable_reason = "user_not_found"

        assert response_status == awaitable_status
        assert response_reason == awaitable_reason

    async def test_no_project(
        self,
        client,
        agent,
        user_repo,
        user_factory,
        floor_factory,
        project_factory,
        building_factory,
        property_factory,
        agent_authorization,
    ):
        c = 0
        properties = []
        for i in range(3):
            project = await project_factory(i=i)
            for j in range(5):
                building = await building_factory(project_id=project.id, i=c)
                floor = await floor_factory(project_id=project.id, building_id=building.id, i=c)
                if j != 2:
                    property = await property_factory(
                        project_id=project.id, building_id=building.id, floor_id=floor.id, i=c
                    )
                else:
                    property = await property_factory(
                        project_id=project.id,
                        building_id=building.id,
                        floor_id=floor.id,
                        type="COMMERCIAL",
                        i=c,
                    )
                properties.append(property)
                user = await user_factory(agent_id=agent.id, i=c)
                c += 1

        headers = {"Authorization": agent_authorization}
        payload = {
            "interested_type": "FLAT",
            "interested_project": project.id + 1,
            "interested": [prop.id for prop in properties[:3]],
        }

        response = await client.patch(
            f"/users/agents/interest/{user.id}", headers=headers, data=dumps(payload)
        )
        response_status = response.status_code
        response_json = response.json()
        response_reason = response_json["reason"]

        awaitable_status = 400
        awaitable_reason = "user_no_project"

        assert response_status == awaitable_status
        assert response_reason == awaitable_reason


@mark.asyncio
class TestAgentsUsersUninterestView(object):
    async def test_success(
        self,
        client,
        agent,
        user_repo,
        user_factory,
        floor_factory,
        project_factory,
        building_factory,
        property_factory,
        agent_authorization,
    ):
        c = 0
        properties = []
        for i in range(3):
            project = await project_factory(i=i)
            for j in range(5):
                building = await building_factory(project_id=project.id, i=c)
                floor = await floor_factory(project_id=project.id, building_id=building.id, i=c)
                if j != 2:
                    property = await property_factory(
                        project_id=project.id, building_id=building.id, floor_id=floor.id, i=c
                    )
                else:
                    property = await property_factory(
                        project_id=project.id,
                        building_id=building.id,
                        floor_id=floor.id,
                        type="COMMERCIAL",
                        i=c,
                    )
                properties.append(property)
                user = await user_factory(agent_id=agent.id, i=c)
                c += 1

        await user_repo.add_m2m(user, "interested", properties)

        user = await user_repo.retrieve({"id": user.id}, prefetch_fields=["interested"])

        awaitable_interested_len = len(properties)

        assert len(user.interested) == awaitable_interested_len

        headers = {"Authorization": agent_authorization}
        payload = {"uninterested": [prop.id for prop in properties[:3]]}

        response = await client.patch(
            f"/users/agents/uninterest/{user.id}", headers=headers, data=dumps(payload)
        )
        response_status = response.status_code

        user = await user_repo.retrieve({"id": user.id}, prefetch_fields=["interested"])

        awaitable_status = 200
        awaitable_interested_len = len(properties) - 3

        assert response_status == awaitable_status
        assert len(user.interested) == awaitable_interested_len

    async def test_not_found(
        self,
        client,
        agent,
        user_repo,
        user_factory,
        floor_factory,
        project_factory,
        building_factory,
        property_factory,
        agent_authorization,
    ):
        c = 0
        properties = []
        for i in range(3):
            project = await project_factory(i=i)
            for j in range(5):
                building = await building_factory(project_id=project.id, i=c)
                floor = await floor_factory(project_id=project.id, building_id=building.id, i=c)
                if j != 2:
                    property = await property_factory(
                        project_id=project.id, building_id=building.id, floor_id=floor.id, i=c
                    )
                else:
                    property = await property_factory(
                        project_id=project.id,
                        building_id=building.id,
                        floor_id=floor.id,
                        type="COMMERCIAL",
                        i=c,
                    )
                properties.append(property)
                user = await user_factory(i=c)
                c += 1

        await user_repo.add_m2m(user, "interested", properties)

        headers = {"Authorization": agent_authorization}
        payload = {"uninterested": [prop.id for prop in properties[:3]]}

        response = await client.patch(
            f"/users/agents/uninterest/{user.id}", headers=headers, data=dumps(payload)
        )
        response_status = response.status_code
        response_json = response.json()
        response_reason = response_json["reason"]

        awaitable_status = 404
        awaitable_reason = "user_not_found"

        assert response_status == awaitable_status
        assert response_reason == awaitable_reason


@mark.asyncio
class TestAgentsUsersCheckView(object):
    async def test_success(self, client, agent, mocker, agent_authorization):
        mocker.patch("src.users.api.user.users_tasks.check_client_unique_task")

        headers = {"Authorization": agent_authorization}
        payload = {
            "name": "test",
            "phone": "+70000000000",
            "email": "lkio@gmail.com",
            "surname": "test",
            "patronymic": "test",
        }

        response = await client.post("/users/agents/check", data=dumps(payload), headers=headers)
        response_status = response.status_code

        awaitable_status = 200

        assert response_status == awaitable_status

    async def test_mismatch(self, client, agent, mocker, user_factory, agent_authorization):
        mocker.patch("src.users.api.user.users_tasks.check_client_unique_task")

        user = await user_factory()

        headers = {"Authorization": agent_authorization}
        payload = {
            "name": "test",
            "phone": "+70000000000",
            "email": user.email,
            "surname": "test",
            "patronymic": "test",
        }

        response = await client.post("/users/agents/check", data=dumps(payload), headers=headers)
        response_status = response.status_code
        response_json = response.json()
        response_reason = response_json["reason"]

        awaitable_status = 400
        awaitable_reason = "user_miss_match"

        assert response_status == awaitable_status
        assert response_reason == awaitable_reason

    async def test_empty_email(self, client, agent, mocker, agent_authorization):
        mocker.patch("src.users.api.user.users_tasks.check_client_unique_task")

        headers = {"Authorization": agent_authorization}
        payload = {
            "name": "test",
            "phone": "+70000000000",
            "email": "",
            "surname": "test",
            "patronymic": "test",
        }

        response = await client.post("/users/agents/check", data=dumps(payload), headers=headers)
        response_status = response.status_code

        awaitable_status = 200

        assert response_status == awaitable_status, response.json()


@mark.asyncio
class TestAgentsUsersLookupView(object):
    async def test_success(self, client, agent, user_factory, agent_authorization):
        for _ in range(15):
            await user_factory(agent_id=agent.id)

        headers = {"Authorization": agent_authorization}

        response = await client.get("/users/agents/lookup", headers=headers)
        response_status = response.status_code
        response_json = response.json()
        response_result = response_json["result"]

        awaitable_status = 200
        awaitable_result_len = 15

        assert response_status == awaitable_status
        assert len(response_result) == awaitable_result_len

        response = await client.get("/users/agents/lookup?search=fsdfsdfsdfsd", headers=headers)
        response_status = response.status_code
        response_json = response.json()
        response_result = response_json["result"]

        awaitable_status = 200
        awaitable_result_len = 0

        assert response_status == awaitable_status
        assert len(response_result) == awaitable_result_len

    async def test_name_search(self, client, agent, user_factory, agent_authorization):
        for _ in range(15):
            await user_factory(agent_id=agent.id)

        headers = {"Authorization": agent_authorization}

        response = await client.get("/users/agents/lookup?search=тест+тест", headers=headers)
        response_status = response.status_code
        response_json = response.json()
        response_type = response_json["type"]["value"]

        awaitable_status = 200
        awaitable_type = "name"

        assert response_status == awaitable_status
        assert response_type == awaitable_type

    async def test_email_search(self, client, agent, user_factory, agent_authorization):
        for _ in range(15):
            await user_factory(agent_id=agent.id)

        headers = {"Authorization": agent_authorization}

        response = await client.get("/users/agents/lookup?search=fsdfsdfsdfsd", headers=headers)
        response_status = response.status_code
        response_json = response.json()
        response_type = response_json["type"]["value"]

        awaitable_status = 200
        awaitable_type = "email"

        assert response_status == awaitable_status
        assert response_type == awaitable_type

    async def test_phone_search(self, client, agent, user_factory, agent_authorization):
        for _ in range(15):
            await user_factory(agent_id=agent.id)

        headers = {"Authorization": agent_authorization}

        response = await client.get("/users/agents/lookup?search=7928", headers=headers)
        response_status = response.status_code
        response_json = response.json()
        response_type = response_json["type"]["value"]

        awaitable_status = 200
        awaitable_type = "phone"

        assert response_status == awaitable_status
        assert response_type == awaitable_type

    async def test_unauthorized(self, client, agent, user_factory):
        for _ in range(15):
            await user_factory(agent_id=agent.id)

        response = await client.get("/users/agents/lookup")
        response_status = response.status_code

        awaitable_status = 401

        assert response_status == awaitable_status


@mark.asyncio
class TestAgentsUsersUnboundView(object):
    async def test_success(
        self, client, agent, user_repo, check_repo, user_factory, check_factory, agent_authorization
    ):
        user = await user_factory()
        check = await check_factory(agent_id=agent.id, user_id=user.id)

        headers = {"Authorization": agent_authorization}

        response = await client.patch(f"/users/agents/unbound/{user.id}", headers=headers)
        response_status = response.status_code

        awaitable_status = 204

        user = await user_repo.retrieve({"id": user.id})
        check = await check_repo.retrieve({"id": check.id})

        assert check is None
        assert user.agent_id is None
        assert response_status == awaitable_status

    async def test_not_found(self, client, agent, user_factory, check_factory, agent_authorization):
        user = await user_factory(agent_id=agent.id)
        await check_factory(agent_id=agent.id, user_id=user.id)

        headers = {"Authorization": agent_authorization}

        response = await client.patch(f"/users/agents/unbound/{user.id + 1}", headers=headers)
        response_status = response.status_code
        response_json = response.json()
        response_reason = response_json["reason"]

        awaitable_status = 404
        awaitable_reason = "user_not_found"

        assert response_status == awaitable_status
        assert response_reason == awaitable_reason

    async def test_unauthorized(self, client, agent, user_factory, check_factory):
        user = await user_factory(agent_id=agent.id)
        await check_factory(agent_id=agent.id, user_id=user.id)

        response = await client.patch(f"/users/agents/unbound/{user.id}")
        response_status = response.status_code

        awaitable_status = 401

        assert response_status == awaitable_status


@mark.asyncio
class TestRepresesUsersListView(object):
    async def test_success(
        self,
        client,
        agent,
        repres,
        property,
        user_factory,
        check_factory,
        booking_factory,
        repres_authorization,
    ):
        for _ in range(15):
            user = await user_factory(agency_id=repres.agency_id, agent_id=agent.id)
            await check_factory(user_id=user.id, agency_id=repres.agency_id)
            for _ in range(4):
                await booking_factory(
                    agency_id=repres.agency_id, user_id=user.id, property=property, decremented=True
                )
            for _ in range(3):
                await booking_factory(
                    agency_id=repres.agency_id,
                    user_id=user.id,
                    property=property,
                    decremented=False,
                )
            for _ in range(2):
                await booking_factory(
                    agency_id=repres.agency_id,
                    active=False,
                    user_id=user.id,
                    property=property,
                    decremented=False,
                )
                await booking_factory(user_id=user.id, property=property, decremented=False)

        headers = {"Authorization": repres_authorization}

        response = await client.get("/users/represes", headers=headers)
        response_status = response.status_code
        response_json = response.json()
        response_count = response_json["count"]
        response_info = response_json["page_info"]
        response_booking_count = response_json["result"][0]["booking_count"]
        response_is_decremented = response_json["result"][0]["is_decremented"]

        awaitable_status = 200
        awaitable_count = 15
        awaitable_booking_count = 7
        awaitable_is_decremented = True

        assert response_count == awaitable_count
        assert response_status == awaitable_status
        assert response_info["next_page"] is not None
        assert response_booking_count == awaitable_booking_count
        assert response_is_decremented == awaitable_is_decremented

    async def test_not_authorized(self, client, agent, repres, user_factory, check_factory):
        for _ in range(15):
            user = await user_factory(agency_id=repres.agency_id, agent_id=agent.id)
            await check_factory(user_id=user.id, agent_id=agent.id)

        response = await client.get("/users/represes")
        response_status = response.status_code

        awaitable_status = 401

        assert response_status == awaitable_status

    async def test_wrong_type(
        self, client, agent, repres, user_factory, check_factory, agent_authorization
    ):
        for _ in range(15):
            user = await user_factory(agency_id=repres.agency_id, agent_id=agent.id)
            await check_factory(user_id=user.id, agent_id=agent.id)

        headers = {"Authorization": agent_authorization}

        response = await client.get("/users/represes", headers=headers)
        response_status = response.status_code

        awaitable_status = 403

        assert response_status == awaitable_status

    async def test_search_filter_success(
        self, client, agent, repres, user_factory, check_factory, repres_authorization
    ):
        for _ in range(15):
            user = await user_factory(agency_id=repres.agency_id, agent_id=agent.id)
            await check_factory(user_id=user.id, agent_id=agent.id)

        email = user.email

        headers = {"Authorization": repres_authorization}

        response = await client.get(f"/users/represes?search={email}", headers=headers)
        response_status = response.status_code
        response_json = response.json()
        response_count = response_json["count"]
        response_info = response_json["page_info"]

        awaitable_status = 200
        awaitable_count = 1

        assert response_count == awaitable_count
        assert response_status == awaitable_status
        assert response_info["next_page"] is None

    async def test_search_filter_fail(
        self, client, agent, repres, user_factory, check_factory, repres_authorization
    ):
        for _ in range(15):
            user = await user_factory(agency_id=repres.agency_id, agent_id=agent.id)
            await check_factory(user_id=user.id, agent_id=agent.id)

        email = user.email

        headers = {"Authorization": repres_authorization}

        response = await client.get(f"/users/represes?search={email}dasdasdas", headers=headers)
        response_status = response.status_code
        response_json = response.json()
        response_count = response_json["count"]
        response_info = response_json["page_info"]

        awaitable_status = 200
        awaitable_count = 0

        assert response_count == awaitable_count
        assert response_status == awaitable_status
        assert response_info["next_page"] is None

    async def test_status_filter_success(
        self,
        client,
        agent,
        repres,
        property,
        user_factory,
        check_factory,
        booking_factory,
        repres_authorization,
    ):
        for i in range(15):
            user = await user_factory(agency_id=repres.agency_id, agent_id=agent.id)
            await check_factory(user_id=user.id, agent_id=agent.id)
            for _ in range(5):
                if i == 5:
                    booking = await booking_factory(
                        user_id=user.id, active=True, property=property, agency_id=repres.agency_id
                    )
                else:
                    booking = await booking_factory(
                        user_id=user.id, active=False, property=property, agency_id=repres.agency_id
                    )

        status = booking.amocrm_stage.value

        headers = {"Authorization": repres_authorization}

        response = await client.get(f"/users/represes?status={status}", headers=headers)
        response_status = response.status_code
        response_json = response.json()
        response_count = response_json["count"]
        response_info = response_json["page_info"]

        awaitable_status = 200
        awaitable_count = 1

        assert response_count == awaitable_count
        assert response_status == awaitable_status
        assert response_info["next_page"] is None

    async def test_status_filter_fail(
        self,
        client,
        agent,
        repres,
        property,
        user_factory,
        check_factory,
        booking_factory,
        repres_authorization,
    ):
        for i in range(15):
            user = await user_factory(agency_id=repres.agency_id, agent_id=agent.id)
            await check_factory(user_id=user.id, agent_id=agent.id)
            for _ in range(5):
                if i == 5:
                    booking = await booking_factory(
                        user_id=user.id, active=False, property=property
                    )
                else:
                    booking = await booking_factory(
                        user_id=user.id, active=False, property=property
                    )

        status = booking.amocrm_stage.value

        headers = {"Authorization": repres_authorization}

        response = await client.get(f"/users/represes?status={status}", headers=headers)
        response_status = response.status_code
        response_json = response.json()
        response_count = response_json["count"]
        response_info = response_json["page_info"]

        awaitable_status = 200
        awaitable_count = 0

        assert response_count == awaitable_count
        assert response_status == awaitable_status
        assert response_info["next_page"] is None

    async def test_work_period_filter_success(
        self, client, agent, repres, user_factory, check_factory, repres_authorization
    ):
        for i in range(15):
            user = await user_factory(agency_id=repres.agency_id, agent_id=agent.id, i=i)
            await check_factory(user_id=user.id, agent_id=agent.id)

        work_period = f"{user.work_start.isoformat()}__{user.work_end.isoformat()}"

        headers = {"Authorization": repres_authorization}

        response = await client.get(f"/users/represes?work_period={work_period}", headers=headers)
        response_status = response.status_code
        response_json = response.json()
        response_count = response_json["count"]
        response_info = response_json["page_info"]

        awaitable_status = 200
        awaitable_count = 1

        assert response_count == awaitable_count
        assert response_status == awaitable_status
        assert response_info["next_page"] is None

    async def test_work_period_filter_fail(
        self, client, agent, repres, user_factory, check_factory, repres_authorization
    ):
        for i in range(15):
            user = await user_factory(agency_id=repres.agency_id, agent_id=agent.id, i=i)
            await check_factory(user_id=user.id, agent_id=agent.id)

        work_period = f"{user.work_start.isoformat()}__fsdfsd{user.work_end.isoformat()}"

        headers = {"Authorization": repres_authorization}

        response = await client.get(f"/users/represes?work_period={work_period}", headers=headers)
        response_status = response.status_code
        response_json = response.json()
        response_count = response_json["count"]
        response_info = response_json["page_info"]

        awaitable_status = 200
        awaitable_count = 15

        assert response_count == awaitable_count
        assert response_status == awaitable_status
        assert response_info["next_page"] is not None

    async def test_property_type_filter_success(
        self,
        client,
        agent,
        repres,
        property,
        user_factory,
        check_factory,
        booking_factory,
        repres_authorization,
    ):
        for i in range(15):
            user = await user_factory(agent_id=agent.id, agency_id=repres.agency_id)
            await check_factory(user_id=user.id, agent_id=agent.id)
            for __ in range(5):
                if i == 5:
                    await booking_factory(
                        user_id=user.id, active=True, property=property, agency_id=repres.agency_id
                    )
                else:
                    await booking_factory(
                        user_id=user.id, active=False, property=property, agency_id=repres.agency_id
                    )

        property_type = property.type.value

        headers = {"Authorization": repres_authorization}

        response = await client.get(
            f"/users/represes?property_type={property_type}", headers=headers
        )
        response_status = response.status_code
        response_json = response.json()
        response_count = response_json["count"]
        response_info = response_json["page_info"]

        awaitable_status = 200
        awaitable_count = 1

        assert response_count == awaitable_count
        assert response_status == awaitable_status
        assert response_info["next_page"] is None

    async def test_property_type_filter_fail(
        self,
        client,
        agent,
        repres,
        property,
        user_factory,
        check_factory,
        booking_factory,
        repres_authorization,
    ):
        for i in range(15):
            user = await user_factory(agent_id=agent.id, agency_id=repres.agency_id)
            await check_factory(user_id=user.id, agent_id=agent.id)
            for __ in range(5):
                if i == 5:
                    await booking_factory(user_id=user.id, active=False, property=property)
                else:
                    await booking_factory(user_id=user.id, active=False, property=property)

        property_type = property.type.value

        headers = {"Authorization": repres_authorization}

        response = await client.get(
            f"/users/represes?property_type={property_type}", headers=headers
        )
        response_status = response.status_code
        response_json = response.json()
        response_count = response_json["count"]
        response_info = response_json["page_info"]

        awaitable_status = 200
        awaitable_count = 0

        assert response_count == awaitable_count
        assert response_status == awaitable_status
        assert response_info["next_page"] is None

    async def test_project_filter_success(
        self,
        client,
        agent,
        repres,
        property,
        user_factory,
        check_factory,
        booking_factory,
        repres_authorization,
    ):
        for i in range(15):
            user = await user_factory(agent_id=agent.id, agency_id=repres.agency_id)
            await check_factory(user_id=user.id, agent_id=agent.id)
            for __ in range(5):
                if i == 5:
                    await booking_factory(
                        user_id=user.id, active=True, property=property, agency_id=repres.agency_id
                    )
                else:
                    await booking_factory(
                        user_id=user.id, active=False, property=property, agency_id=repres.agency_id
                    )

        project = property.project.slug

        headers = {"Authorization": repres_authorization}

        response = await client.get(f"/users/represes?project={project}", headers=headers)
        response_status = response.status_code
        response_json = response.json()
        response_count = response_json["count"]
        response_info = response_json["page_info"]

        awaitable_status = 200
        awaitable_count = 1

        assert response_count == awaitable_count
        assert response_status == awaitable_status
        assert response_info["next_page"] is None

    async def test_project_filter_fail(
        self,
        client,
        agent,
        repres,
        property,
        user_factory,
        check_factory,
        booking_factory,
        repres_authorization,
    ):
        for i in range(15):
            user = await user_factory(agent_id=agent.id, agency_id=repres.agency_id)
            await check_factory(user_id=user.id, agent_id=agent.id)
            for __ in range(5):
                if i == 5:
                    await booking_factory(user_id=user.id, active=False, property=property)
                else:
                    await booking_factory(user_id=user.id, active=False, property=property)

        project = property.project.slug

        headers = {"Authorization": repres_authorization}

        response = await client.get(f"/users/represes?project={project}", headers=headers)
        response_status = response.status_code
        response_json = response.json()
        response_count = response_json["count"]
        response_info = response_json["page_info"]

        awaitable_status = 200
        awaitable_count = 0

        assert response_count == awaitable_count
        assert response_status == awaitable_status
        assert response_info["next_page"] is None


@mark.asyncio
class TestRepresesUsersRetrieveView(object):
    async def test_success(
        self,
        client,
        agent,
        repres,
        booking,
        property,
        user_repo,
        user_factory,
        booking_repo,
        check_factory,
        repres_authorization,
    ):
        user = await user_factory(agent_id=agent.id, agency_id=repres.agency_id)
        await check_factory(agency_id=repres.agency_id, user_id=user.id)
        await booking_repo.update(booking, {"user_id": user.id, "agency_id": repres.agency_id})
        await user_repo.add_m2m(user, "interested", [property])

        headers = {"Authorization": repres_authorization}

        response = await client.get(f"/users/represes/{user.id}", headers=headers)
        response_status = response.status_code
        response_json = response.json()
        response_indents = response_json["indents"]
        response_interesting = response_json["interesting"]

        awaitable_status = 200

        assert response_indents
        assert response_interesting
        assert response_status == awaitable_status

    async def test_fail(self, client, user_factory, agent, repres, repres_authorization):
        user = await user_factory(agent_id=agent.id)

        headers = {"Authorization": repres_authorization}

        response = await client.get(f"/users/represes/{user.id}", headers=headers)
        response_status = response.status_code
        response_json = response.json()
        response_reason = response_json["reason"]

        awaitable_status = 404
        awaitable_reason = "user_not_found"

        assert response_status == awaitable_status
        assert response_reason == awaitable_reason


@mark.asyncio
class TestRepresesAgentsUsersRetrieveView(object):
    async def test_success(
        self,
        client,
        agent,
        repres,
        booking,
        property,
        user_repo,
        user_factory,
        booking_repo,
        check_factory,
        repres_authorization,
    ):
        user = await user_factory(agency_id=repres.agency_id)
        await check_factory(agent_id=agent.id, user_id=user.id)
        await booking_repo.update(booking, {"user_id": user.id, "agency_id": repres.agency_id})
        await user_repo.add_m2m(user, "interested", [property])

        headers = {"Authorization": repres_authorization}

        response = await client.get(f"/users/represes/{user.id}/{agent.id}", headers=headers)
        response_status = response.status_code
        response_json = response.json()
        response_indents = response_json["indents"]
        response_interesting = response_json["interesting"]

        awaitable_status = 200

        assert not response_interesting
        assert not response_indents
        assert response_status == awaitable_status

        user = await user_factory(agency_id=repres.agency_id, agent_id=agent.id)
        await check_factory(agent_id=agent.id, user_id=user.id)
        await booking_repo.update(
            booking, {"user_id": user.id, "agency_id": repres.agency_id, "agent_id": agent.id}
        )
        await user_repo.add_m2m(user, "interested", [property])

        headers = {"Authorization": repres_authorization}

        response = await client.get(f"/users/represes/{user.id}/{agent.id}", headers=headers)
        response_status = response.status_code
        response_json = response.json()
        response_indents = response_json["indents"]
        response_interesting = response_json["interesting"]

        awaitable_status = 200

        assert response_interesting
        assert response_indents
        assert response_status == awaitable_status

    async def test_fail(
        self,
        client,
        agent,
        repres,
        booking,
        property,
        user_repo,
        user_factory,
        booking_repo,
        check_factory,
        repres_authorization,
    ):
        user = await user_factory(agency_id=repres.agency_id)
        await check_factory(agent_id=agent.id, user_id=user.id)
        await booking_repo.update(booking, {"user_id": user.id, "agency_id": repres.agency_id})
        await user_repo.add_m2m(user, "interested", [property])

        headers = {"Authorization": repres_authorization}

        response = await client.get(f"/users/represes/{user.id}/{agent.id + 1}", headers=headers)
        response_status = response.status_code
        response_json = response.json()
        response_reason = response_json["reason"]

        awaitable_status = 404
        awaitable_reason = "user_not_found"

        assert response_status == awaitable_status
        assert response_reason == awaitable_reason


@mark.asyncio
class TestRepresesUsersSpecsView(object):
    async def test_success(
        self,
        client,
        agent,
        repres,
        user_factory,
        floor_factory,
        booking_factory,
        project_factory,
        property_factory,
        building_factory,
        repres_authorization,
    ):
        c = 0
        for i in range(3):
            project = await project_factory(i=i)
            for j in range(5):
                building = await building_factory(project_id=project.id, i=c)
                floor = await floor_factory(project_id=project.id, building_id=building.id, i=c)
                if j != 2:
                    property = await property_factory(
                        project_id=project.id, building_id=building.id, floor_id=floor.id, i=c
                    )
                else:
                    property = await property_factory(
                        project_id=project.id,
                        building_id=building.id,
                        floor_id=floor.id,
                        type="COMMERCIAL",
                        i=c,
                    )
                user = await user_factory(agent_id=agent.id, i=c, agency_id=repres.agency_id)
                if j != 2:
                    await booking_factory(
                        property=property,
                        building=building,
                        user_id=user.id,
                        i=c,
                        agency_id=repres.agency_id,
                    )
                elif j == 3:
                    await booking_factory(
                        property=property,
                        building=building,
                        user_id=user.id,
                        amocrm_stage="ddu_unregistered",
                        i=c,
                        active=False,
                        agency_id=repres.agency_id,
                    )
                else:
                    await booking_factory(
                        property=property,
                        building=building,
                        user_id=user.id,
                        amocrm_stage="booking",
                        i=c,
                        agency_id=repres.agency_id,
                    )
                c += 1

        headers = {"Authorization": repres_authorization}

        response = await client.get("/users/represes/specs", headers=headers)
        response_status = response.status_code
        response_json = response.json()
        response_ordering = response_json["ordering"]
        response_specs = response_json["specs"]

        awaitable_status = 200
        awaitable_specs_len = 5
        awaitable_ordering_len = 4

        assert response_specs.get("agent")
        assert response_specs.get("status")
        assert response_specs.get("project")
        assert response_specs.get("work_period")
        assert response_specs.get("property_type")
        assert response_status == awaitable_status
        assert len(response_specs) == awaitable_specs_len
        assert len(response_ordering) == awaitable_ordering_len

    async def test_fail(
        self,
        client,
        agent,
        repres,
        user_factory,
        floor_factory,
        booking_factory,
        project_factory,
        property_factory,
        building_factory,
        repres_authorization,
    ):
        c = 0
        for i in range(3):
            project = await project_factory(i=i)
            for j in range(5):
                building = await building_factory(project_id=project.id, i=c)
                floor = await floor_factory(project_id=project.id, building_id=building.id, i=c)
                if j != 2:
                    property = await property_factory(
                        project_id=project.id, building_id=building.id, floor_id=floor.id, i=c
                    )
                else:
                    property = await property_factory(
                        project_id=project.id,
                        building_id=building.id,
                        floor_id=floor.id,
                        type="COMMERCIAL",
                        i=c,
                    )
                user = await user_factory(agent_id=None, i=c)
                if j != 2:
                    await booking_factory(
                        property=property, building=building, user_id=user.id, i=c
                    )
                elif j == 3:
                    await booking_factory(
                        property=property,
                        building=building,
                        user_id=user.id,
                        amocrm_stage="ddu_unregistered",
                        i=c,
                        active=False,
                    )
                else:
                    await booking_factory(
                        property=property,
                        building=building,
                        user_id=user.id,
                        amocrm_stage="booking",
                        i=c,
                    )
                c += 1

        headers = {"Authorization": repres_authorization}

        response = await client.get("/users/represes/specs", headers=headers)
        response_status = response.status_code
        response_json = response.json()
        response_ordering = response_json["ordering"]
        response_specs = response_json["specs"]

        awaitable_status = 200
        awaitable_specs_len = 5
        awaitable_ordering_len = 4

        assert not response_specs.get("agent")
        assert not response_specs.get("status")
        assert not response_specs.get("project")
        assert response_status == awaitable_status
        assert not response_specs.get("work_period")
        assert not response_specs.get("property_type")
        assert len(response_specs) == awaitable_specs_len
        assert len(response_ordering) == awaitable_ordering_len


@mark.asyncio
class TestRepresesUsersFacetsView(object):
    async def test_success(
        self,
        client,
        agent,
        repres,
        user_factory,
        floor_factory,
        booking_factory,
        project_factory,
        property_factory,
        building_factory,
        repres_authorization,
    ):
        c = 0
        for i in range(3):
            project = await project_factory(i=i)
            for j in range(5):
                building = await building_factory(project_id=project.id, i=c)
                floor = await floor_factory(project_id=project.id, building_id=building.id, i=c)
                if j != 2:
                    property = await property_factory(
                        project_id=project.id, building_id=building.id, floor_id=floor.id, i=c
                    )
                else:
                    property = await property_factory(
                        project_id=project.id,
                        building_id=building.id,
                        floor_id=floor.id,
                        type="COMMERCIAL",
                        i=c,
                    )
                user = await user_factory(agent_id=agent.id, i=c, agency_id=repres.agency_id)
                if j != 2:
                    await booking_factory(
                        property=property,
                        building=building,
                        user_id=user.id,
                        i=c,
                        agency_id=repres.agency_id,
                    )
                elif j == 3:
                    await booking_factory(
                        property=property,
                        building=building,
                        user_id=user.id,
                        amocrm_stage="ddu_unregistered",
                        i=c,
                        active=False,
                        agency_id=repres.agency_id,
                    )
                else:
                    await booking_factory(
                        property=property,
                        building=building,
                        user_id=user.id,
                        amocrm_stage="booking",
                        i=c,
                        agency_id=repres.agency_id,
                    )
                c += 1

        headers = {"Authorization": repres_authorization}

        response = await client.get("/users/represes/facets", headers=headers)
        response_status = response.status_code
        response_json = response.json()
        response_count = response_json["count"]
        response_facets = response_json["facets"]

        awaitable_count = 15
        awaitable_status = 200
        awaitable_facets_len = 5

        assert response_facets.get("agent")
        assert response_facets.get("status")
        assert response_facets.get("project")
        assert response_count == awaitable_count
        assert response_facets.get("work_period")
        assert response_facets.get("property_type")
        assert response_status == awaitable_status
        assert len(response_facets) == awaitable_facets_len

    async def test_success_filtered(
        self,
        client,
        agent,
        repres,
        user_factory,
        floor_factory,
        booking_factory,
        project_factory,
        property_factory,
        building_factory,
        repres_authorization,
    ):
        c = 0
        for i in range(3):
            project = await project_factory(i=i)
            for j in range(5):
                building = await building_factory(project_id=project.id, i=c)
                floor = await floor_factory(project_id=project.id, building_id=building.id, i=c)
                if j != 2:
                    property = await property_factory(
                        project_id=project.id, building_id=building.id, floor_id=floor.id, i=c
                    )
                else:
                    property = await property_factory(
                        project_id=project.id,
                        building_id=building.id,
                        floor_id=floor.id,
                        type="COMMERCIAL",
                        i=c,
                    )
                user = await user_factory(agent_id=agent.id, i=c, agency_id=repres.agency_id)
                if j != 2:
                    await booking_factory(
                        property=property,
                        building=building,
                        user_id=user.id,
                        i=c,
                        agency_id=repres.agency_id,
                    )
                elif j == 3:
                    await booking_factory(
                        property=property,
                        building=building,
                        user_id=user.id,
                        amocrm_stage="ddu_unregistered",
                        i=c,
                        active=False,
                        agency_id=repres.agency_id,
                    )
                else:
                    await booking_factory(
                        property=property,
                        building=building,
                        user_id=user.id,
                        amocrm_stage="booking",
                        i=c,
                        agency_id=repres.agency_id,
                    )
                c += 1

        headers = {"Authorization": repres_authorization}

        response = await client.get(
            f"/users/represes/facets?project={project.slug}", headers=headers
        )
        response_status = response.status_code
        response_json = response.json()
        response_count = response_json["count"]
        response_facets = response_json["facets"]

        awaitable_count = 5
        awaitable_status = 200
        awaitable_facets_len = 5

        assert response_facets.get("agent")
        assert response_facets.get("status")
        assert response_facets.get("project")
        assert response_count == awaitable_count
        assert response_facets.get("work_period")
        assert response_facets.get("property_type")
        assert response_status == awaitable_status
        assert len(response_facets) == awaitable_facets_len

    async def test_fail(
        self,
        client,
        agent,
        repres,
        user_factory,
        floor_factory,
        booking_factory,
        project_factory,
        property_factory,
        building_factory,
        repres_authorization,
    ):
        c = 0
        for i in range(3):
            project = await project_factory(i=i)
            for j in range(5):
                building = await building_factory(project_id=project.id, i=c)
                floor = await floor_factory(project_id=project.id, building_id=building.id, i=c)
                if j != 2:
                    property = await property_factory(
                        project_id=project.id, building_id=building.id, floor_id=floor.id, i=c
                    )
                else:
                    property = await property_factory(
                        project_id=project.id,
                        building_id=building.id,
                        floor_id=floor.id,
                        type="COMMERCIAL",
                        i=c,
                    )
                user = await user_factory(agent_id=None, i=c, agency_id=None)
                if j != 2:
                    await booking_factory(
                        property=property, building=building, user_id=user.id, i=c
                    )
                elif j == 3:
                    await booking_factory(
                        property=property,
                        building=building,
                        user_id=user.id,
                        amocrm_stage="ddu_unregistered",
                        i=c,
                        active=False,
                    )
                else:
                    await booking_factory(
                        property=property,
                        building=building,
                        user_id=user.id,
                        amocrm_stage="booking",
                        i=c,
                    )
                c += 1

        headers = {"Authorization": repres_authorization}

        response = await client.get(
            f"/users/represes/facets?project={project.slug}", headers=headers
        )
        response_status = response.status_code
        response_json = response.json()
        response_count = response_json["count"]
        response_facets = response_json["facets"]

        awaitable_count = 0
        awaitable_status = 200
        awaitable_facets_len = 5

        assert not response_facets.get("agent")
        assert not response_facets.get("status")
        assert not response_facets.get("project")
        assert response_count == awaitable_count
        assert response_status == awaitable_status
        assert not response_facets.get("work_period")
        assert not response_facets.get("property_type")
        assert len(response_facets) == awaitable_facets_len


@mark.asyncio
class TestAgentsUsersInterestView(object):
    async def test_success(
        self,
        client,
        agent,
        repres,
        user_repo,
        user_factory,
        floor_factory,
        project_factory,
        building_factory,
        property_factory,
        repres_authorization,
    ):
        c = 0
        properties = []
        for i in range(3):
            project = await project_factory(i=i)
            for j in range(5):
                building = await building_factory(project_id=project.id, i=c)
                floor = await floor_factory(project_id=project.id, building_id=building.id, i=c)
                if j != 2:
                    property = await property_factory(
                        project_id=project.id, building_id=building.id, floor_id=floor.id, i=c
                    )
                else:
                    property = await property_factory(
                        project_id=project.id,
                        building_id=building.id,
                        floor_id=floor.id,
                        type="COMMERCIAL",
                        i=c,
                    )
                properties.append(property)
                user = await user_factory(agent_id=agent.id, i=c, agency_id=repres.agency_id)
                c += 1

        user = await user_repo.retrieve({"id": user.id}, prefetch_fields=["interested"])

        awaitable_interested_len = 0

        assert len(user.interested) == awaitable_interested_len

        headers = {"Authorization": repres_authorization}
        payload = {
            "interested_type": "FLAT",
            "interested_project": project.id,
            "interested": [prop.id for prop in properties[:3]],
        }

        response = await client.patch(
            f"/users/represes/interest/{user.id}", headers=headers, data=dumps(payload)
        )
        response_status = response.status_code

        user = await user_repo.retrieve({"id": user.id}, prefetch_fields=["interested"])

        awaitable_status = 200
        awaitable_interested_len = 3
        awaitable_interested_type = "FLAT"
        awaitable_interested_project = project.id

        assert response_status == awaitable_status
        assert len(user.interested) == awaitable_interested_len
        assert user.interested_type == awaitable_interested_type
        assert user.interested_project_id == awaitable_interested_project

    async def test_no_duplicates(
        self,
        client,
        agent,
        repres,
        user_repo,
        user_factory,
        floor_factory,
        project_factory,
        building_factory,
        property_factory,
        repres_authorization,
    ):
        c = 0
        properties = []
        for i in range(3):
            project = await project_factory(i=i)
            for j in range(5):
                building = await building_factory(project_id=project.id, i=c)
                floor = await floor_factory(project_id=project.id, building_id=building.id, i=c)
                if j != 2:
                    property = await property_factory(
                        project_id=project.id, building_id=building.id, floor_id=floor.id, i=c
                    )
                else:
                    property = await property_factory(
                        project_id=project.id,
                        building_id=building.id,
                        floor_id=floor.id,
                        type="COMMERCIAL",
                        i=c,
                    )
                properties.append(property)
                user = await user_factory(agent_id=agent.id, i=c, agency_id=repres.agency_id)
                c += 1

        user = await user_repo.retrieve({"id": user.id}, prefetch_fields=["interested"])

        awaitable_interested_len = 0

        assert len(user.interested) == awaitable_interested_len

        headers = {"Authorization": repres_authorization}
        payload = {
            "interested_type": "FLAT",
            "interested_project": project.id,
            "interested": [prop.id for prop in properties[:3]],
        }

        response = await client.patch(
            f"/users/represes/interest/{user.id}", headers=headers, data=dumps(payload)
        )
        response_status = response.status_code

        user = await user_repo.retrieve({"id": user.id}, prefetch_fields=["interested"])

        awaitable_status = 200
        awaitable_interested_len = 3
        awaitable_interested_type = "FLAT"
        awaitable_interested_project = project.id

        assert response_status == awaitable_status
        assert len(user.interested) == awaitable_interested_len
        assert user.interested_type == awaitable_interested_type
        assert user.interested_project_id == awaitable_interested_project

        response = await client.patch(
            f"/users/represes/interest/{user.id}", headers=headers, data=dumps(payload)
        )
        response_status = response.status_code

        user = await user_repo.retrieve({"id": user.id}, prefetch_fields=["interested"])

        awaitable_status = 200
        awaitable_interested_len = 3
        awaitable_interested_type = "FLAT"
        awaitable_interested_project = project.id

        assert response_status == awaitable_status
        assert len(user.interested) == awaitable_interested_len
        assert user.interested_type == awaitable_interested_type
        assert user.interested_project_id == awaitable_interested_project

    async def test_not_found(
        self,
        client,
        agent,
        user_repo,
        user_factory,
        floor_factory,
        project_factory,
        building_factory,
        property_factory,
        repres_authorization,
    ):
        c = 0
        properties = []
        for i in range(3):
            project = await project_factory(i=i)
            for j in range(5):
                building = await building_factory(project_id=project.id, i=c)
                floor = await floor_factory(project_id=project.id, building_id=building.id, i=c)
                if j != 2:
                    property = await property_factory(
                        project_id=project.id, building_id=building.id, floor_id=floor.id, i=c
                    )
                else:
                    property = await property_factory(
                        project_id=project.id,
                        building_id=building.id,
                        floor_id=floor.id,
                        type="COMMERCIAL",
                        i=c,
                    )
                properties.append(property)
                user = await user_factory(i=c)
                c += 1

        headers = {"Authorization": repres_authorization}
        payload = {
            "interested_type": "FLAT",
            "interested_project": project.id,
            "interested": [prop.id for prop in properties[:3]],
        }

        response = await client.patch(
            f"/users/represes/interest/{user.id}", headers=headers, data=dumps(payload)
        )
        response_status = response.status_code
        response_json = response.json()
        response_reason = response_json["reason"]

        awaitable_status = 404
        awaitable_reason = "user_not_found"

        assert response_status == awaitable_status
        assert response_reason == awaitable_reason

    async def test_no_project(
        self,
        client,
        agent,
        repres,
        user_repo,
        user_factory,
        floor_factory,
        project_factory,
        building_factory,
        property_factory,
        repres_authorization,
    ):
        c = 0
        properties = []
        for i in range(3):
            project = await project_factory(i=i)
            for j in range(5):
                building = await building_factory(project_id=project.id, i=c)
                floor = await floor_factory(project_id=project.id, building_id=building.id, i=c)
                if j != 2:
                    property = await property_factory(
                        project_id=project.id, building_id=building.id, floor_id=floor.id, i=c
                    )
                else:
                    property = await property_factory(
                        project_id=project.id,
                        building_id=building.id,
                        floor_id=floor.id,
                        type="COMMERCIAL",
                        i=c,
                    )
                properties.append(property)
                user = await user_factory(agent_id=agent.id, i=c, agency_id=repres.agency_id)
                c += 1

        headers = {"Authorization": repres_authorization}
        payload = {
            "interested_type": "FLAT",
            "interested_project": project.id + 1,
            "interested": [prop.id for prop in properties[:3]],
        }

        response = await client.patch(
            f"/users/represes/interest/{user.id}", headers=headers, data=dumps(payload)
        )
        response_status = response.status_code
        response_json = response.json()
        response_reason = response_json["reason"]

        awaitable_status = 400
        awaitable_reason = "user_no_project"

        assert response_status == awaitable_status
        assert response_reason == awaitable_reason


@mark.asyncio
class TestRepresesUsersUninterestView(object):
    async def test_success(
        self,
        client,
        agent,
        repres,
        user_repo,
        user_factory,
        floor_factory,
        project_factory,
        building_factory,
        property_factory,
        repres_authorization,
    ):
        c = 0
        properties = []
        for i in range(3):
            project = await project_factory(i=i)
            for j in range(5):
                building = await building_factory(project_id=project.id, i=c)
                floor = await floor_factory(project_id=project.id, building_id=building.id, i=c)
                if j != 2:
                    property = await property_factory(
                        project_id=project.id, building_id=building.id, floor_id=floor.id, i=c
                    )
                else:
                    property = await property_factory(
                        project_id=project.id,
                        building_id=building.id,
                        floor_id=floor.id,
                        type="COMMERCIAL",
                        i=c,
                    )
                properties.append(property)
                user = await user_factory(agent_id=agent.id, i=c, agency_id=repres.agency_id)
                c += 1

        await user_repo.add_m2m(user, "interested", properties)

        user = await user_repo.retrieve({"id": user.id}, prefetch_fields=["interested"])

        awaitable_interested_len = len(properties)

        assert len(user.interested) == awaitable_interested_len

        headers = {"Authorization": repres_authorization}
        payload = {"uninterested": [prop.id for prop in properties[:3]]}

        response = await client.patch(
            f"/users/represes/uninterest/{user.id}", headers=headers, data=dumps(payload)
        )
        response_status = response.status_code

        user = await user_repo.retrieve({"id": user.id}, prefetch_fields=["interested"])

        awaitable_status = 200
        awaitable_interested_len = len(properties) - 3

        assert response_status == awaitable_status
        assert len(user.interested) == awaitable_interested_len

    async def test_not_found(
        self,
        client,
        agent,
        repres,
        user_repo,
        user_factory,
        floor_factory,
        project_factory,
        building_factory,
        property_factory,
        repres_authorization,
    ):
        c = 0
        properties = []
        for i in range(3):
            project = await project_factory(i=i)
            for j in range(5):
                building = await building_factory(project_id=project.id, i=c)
                floor = await floor_factory(project_id=project.id, building_id=building.id, i=c)
                if j != 2:
                    property = await property_factory(
                        project_id=project.id, building_id=building.id, floor_id=floor.id, i=c
                    )
                else:
                    property = await property_factory(
                        project_id=project.id,
                        building_id=building.id,
                        floor_id=floor.id,
                        type="COMMERCIAL",
                        i=c,
                    )
                properties.append(property)
                user = await user_factory(i=c)
                c += 1

        await user_repo.add_m2m(user, "interested", properties)

        headers = {"Authorization": repres_authorization}
        payload = {"uninterested": [prop.id for prop in properties[:3]]}

        response = await client.patch(
            f"/users/represes/uninterest/{user.id}", headers=headers, data=dumps(payload)
        )
        response_status = response.status_code
        response_json = response.json()
        response_reason = response_json["reason"]

        awaitable_status = 404
        awaitable_reason = "user_not_found"

        assert response_status == awaitable_status
        assert response_reason == awaitable_reason


@mark.asyncio
class TestRepresesUsersLookupView(object):
    async def test_success(self, client, agent, repres, user_factory, repres_authorization):
        for _ in range(15):
            await user_factory(agent_id=agent.id, agency_id=repres.agency_id)

        headers = {"Authorization": repres_authorization}

        response = await client.get("/users/represes/lookup", headers=headers)
        response_status = response.status_code
        response_json = response.json()
        response_result = response_json["result"]

        awaitable_status = 200
        awaitable_result_len = 15

        assert response_status == awaitable_status
        assert len(response_result) == awaitable_result_len

        response = await client.get("/users/represes/lookup?search=fsdfsdfsdfsd", headers=headers)
        response_status = response.status_code
        response_json = response.json()
        response_result = response_json["result"]

        awaitable_status = 200
        awaitable_result_len = 0

        assert response_status == awaitable_status
        assert len(response_result) == awaitable_result_len

    async def test_name_search(self, client, agent, repres, user_factory, repres_authorization):
        for _ in range(15):
            await user_factory(agent_id=agent.id, agency_id=repres.agency_id)

        headers = {"Authorization": repres_authorization}

        response = await client.get("/users/represes/lookup?search=тест+тест", headers=headers)
        response_status = response.status_code
        response_json = response.json()
        response_type = response_json["type"]["value"]

        awaitable_status = 200
        awaitable_type = "name"

        assert response_status == awaitable_status
        assert response_type == awaitable_type

    async def test_email_search(self, client, agent, repres, user_factory, repres_authorization):
        for _ in range(15):
            await user_factory(agent_id=agent.id, agency_id=repres.agency_id)

        headers = {"Authorization": repres_authorization}

        response = await client.get("/users/represes/lookup?search=fsdfsdfsdfsd", headers=headers)
        response_status = response.status_code
        response_json = response.json()
        response_type = response_json["type"]["value"]

        awaitable_status = 200
        awaitable_type = "email"

        assert response_status == awaitable_status
        assert response_type == awaitable_type

    async def test_phone_search(self, client, agent, repres, user_factory, repres_authorization):
        for _ in range(15):
            await user_factory(agent_id=agent.id, agency_id=repres.agency_id)

        headers = {"Authorization": repres_authorization}

        response = await client.get("/users/represes/lookup?search=7928", headers=headers)
        response_status = response.status_code
        response_json = response.json()
        response_type = response_json["type"]["value"]

        awaitable_status = 200
        awaitable_type = "phone"

        assert response_status == awaitable_status
        assert response_type == awaitable_type

    async def test_unauthorized(self, client, agent, repres, user_factory):
        for _ in range(15):
            await user_factory(agent_id=agent.id, agency_id=repres.agency_id)

        response = await client.get("/users/represes/lookup")
        response_status = response.status_code

        awaitable_status = 401

        assert response_status == awaitable_status


@mark.asyncio
class TestRepresesUsersBoundView(object):
    async def test_success(
        self,
        client,
        agent,
        repres,
        mocker,
        user_repo,
        check_repo,
        user_factory,
        check_factory,
        repres_authorization,
    ):
        mocker.patch("src.users.api.user.users_tasks.change_client_agent_task")
        user = await user_factory(agency_id=repres.agency_id)
        check = await check_factory(user_id=user.id, agency_id=repres.agency_id, status="unique")

        headers = {"Authorization": repres_authorization}

        payload = {"agent_id": agent.id}

        response = await client.patch(
            f"/users/represes/bound/{user.id}", headers=headers, data=dumps(payload)
        )
        response_status = response.status_code

        user = await user_repo.retrieve({"id": user.id})
        check = await check_repo.retrieve({"id": check.id})

        awaitable_status = 204

        assert user.agent_id == agent.id
        assert check.agent_id == agent.id
        assert response_status == awaitable_status

    async def test_no_agent(
        self,
        client,
        agent,
        repres,
        user_repo,
        check_repo,
        user_factory,
        check_factory,
        repres_authorization,
    ):
        user = await user_factory(agency_id=repres.agency_id)
        await check_factory(user_id=user.id, agency_id=repres.agency_id, status="unique")

        headers = {"Authorization": repres_authorization}

        payload = {"agent_id": 99823}

        response = await client.patch(
            f"/users/represes/bound/{user.id}", headers=headers, data=dumps(payload)
        )
        response_status = response.status_code
        response_json = response.json()
        response_reason = response_json["reason"]

        awaitable_status = 404
        awaitable_reason = "user_no_agent"

        assert response_status == awaitable_status
        assert response_reason == awaitable_reason

    async def test_not_found(
        self,
        client,
        agent,
        repres,
        user_repo,
        check_repo,
        user_factory,
        check_factory,
        repres_authorization,
    ):
        user = await user_factory(agency_id=repres.agency_id)
        await check_factory(user_id=user.id, agency_id=repres.agency_id, status="unique")

        headers = {"Authorization": repres_authorization}

        payload = {"agent_id": agent.id}

        response = await client.patch(
            "/users/represes/bound/89734", headers=headers, data=dumps(payload)
        )
        response_status = response.status_code
        response_json = response.json()
        response_reason = response_json["reason"]

        awaitable_status = 404
        awaitable_reason = "user_not_found"

        assert response_status == awaitable_status
        assert response_reason == awaitable_reason

    async def test_already_bound(
        self,
        client,
        agent,
        repres,
        user_repo,
        check_repo,
        user_factory,
        check_factory,
        repres_authorization,
    ):
        user = await user_factory(agency_id=repres.agency_id)
        await check_factory(
            user_id=user.id, agency_id=repres.agency_id, status="unique", agent_id=agent.id
        )

        headers = {"Authorization": repres_authorization}

        payload = {"agent_id": agent.id}

        response = await client.patch(
            f"/users/represes/bound/{user.id}", headers=headers, data=dumps(payload)
        )
        response_status = response.status_code
        response_json = response.json()
        response_reason = response_json["reason"]

        awaitable_status = 404
        awaitable_reason = "user_not_found"

        assert response_status == awaitable_status
        assert response_reason == awaitable_reason

    async def test_unauthorized(
        self, client, agent, repres, user_repo, check_repo, user_factory, check_factory
    ):
        user = await user_factory(agency_id=repres.agency_id)
        await check_factory(
            user_id=user.id, agency_id=repres.agency_id, status="unique", agent_id=agent.id
        )

        payload = {"agent_id": agent.id}

        response = await client.patch(f"/users/represes/bound/{user.id}", data=dumps(payload))
        response_status = response.status_code

        awaitable_status = 401

        assert response_status == awaitable_status


@mark.asyncio
class TestRepresesUsersUnboundView(object):
    async def test_success(
        self,
        client,
        agent,
        repres,
        user_repo,
        check_repo,
        user_factory,
        check_factory,
        repres_authorization,
    ):
        user = await user_factory(agent_id=agent.id, agency_id=repres.agency_id)
        check = await check_factory(
            agent_id=agent.id, user_id=user.id, agency_id=repres.agency_id, status="unique"
        )

        headers = {"Authorization": repres_authorization}
        payload = {"agent_id": agent.id}

        response = await client.patch(
            f"/users/represes/unbound/{user.id}", data=dumps(payload), headers=headers
        )
        response_status = response.status_code

        awaitable_status = 204

        user = await user_repo.retrieve({"id": user.id})
        check = await check_repo.retrieve({"id": check.id})

        assert user.agent_id is None
        assert check.agent_id is None
        assert response_status == awaitable_status

    async def test_not_found(
        self,
        client,
        agent,
        repres,
        user_repo,
        check_repo,
        user_factory,
        check_factory,
        repres_authorization,
    ):
        user = await user_factory(agent_id=agent.id)
        await check_factory(
            agent_id=agent.id, user_id=user.id, agency_id=repres.agency_id, status="unique"
        )
        payload = {"agent_id": agent.id}

        headers = {"Authorization": repres_authorization}

        response = await client.patch(
            f"/users/represes/unbound/{user.id + 1}", data=dumps(payload), headers=headers
        )
        response_status = response.status_code
        response_json = response.json()
        response_reason = response_json["reason"]

        awaitable_status = 404
        awaitable_reason = "user_not_found"

        assert response_status == awaitable_status
        assert response_reason == awaitable_reason

    async def test_unauthorized(self, client, agent, repres, user_factory, check_factory):
        user = await user_factory(agent_id=agent.id, agency_id=repres.agency_id)
        await check_factory(
            agent_id=agent.id, user_id=user.id, agency_id=repres.agency_id, status="unique"
        )

        response = await client.patch(f"/users/represes/unbound/{user.id}")
        response_status = response.status_code

        awaitable_status = 401

        assert response_status == awaitable_status


@mark.asyncio
class TestRepresesUsersCheckView(object):
    async def test_success(
        self, client, repres, mocker, user_repo, check_repo, repres_authorization, user
    ):
        check_mock = mocker.patch("src.users.api.user.services.CheckUniqueService.__call__")
        check_mock.return_value = True

        checks = await check_repo.list({"agency_id": repres.agency_id})

        assert not checks

        headers = {"Authorization": repres_authorization}
        payload = {
            "name": "test",
            "phone": "+70000000000",
            "email": "lkio@gmail.com",
            "surname": "test",
            "patronymic": "test",
        }

        response = await client.post("/users/represes/check", data=dumps(payload), headers=headers)
        response_status = response.status_code

        checks = await check_repo.list({"agency_id": repres.agency_id})
        check = checks[0]

        awaitable_status = 200
        awaitable_checks_len = 1
        awaitable_check_status = "unique"

        assert user.agency_id == repres.agency_id
        assert response_status == awaitable_status
        assert len(checks) == awaitable_checks_len
        assert check.status.value == awaitable_check_status

    async def test_mismatch(self, client, repres, mocker, user_factory, repres_authorization):
        check_mock = mocker.patch("src.users.api.user.services.CheckUniqueService.__call__")
        check_mock.return_value = True

        user = await user_factory()

        headers = {"Authorization": repres_authorization}
        payload = {
            "name": "test",
            "phone": "+70000000000",
            "email": user.email,
            "surname": "test",
            "patronymic": "test",
        }

        response = await client.post("/users/represes/check", data=dumps(payload), headers=headers)
        response_status = response.status_code
        response_json = response.json()
        response_reason = response_json["reason"]

        awaitable_status = 400
        awaitable_reason = "user_miss_match"

        assert response_status == awaitable_status
        assert response_reason == awaitable_reason

    async def test_no_duplicates(
        self, client, repres, mocker, user_repo, check_repo, repres_authorization, user
    ):
        check_mock = mocker.patch("src.users.api.user.services.CheckUniqueService.__call__")
        check_mock.return_value = True

        checks = await check_repo.list({"agency_id": repres.agency_id})

        assert not checks

        headers = {"Authorization": repres_authorization}
        payload = {
            "name": "test",
            "phone": "+70000000000",
            "email": "lkio@gmail.com",
            "surname": "test",
            "patronymic": "test",
        }

        response = await client.post("/users/represes/check", data=dumps(payload), headers=headers)
        response_status = response.status_code

        checks = await check_repo.list({"agency_id": repres.agency_id})
        check = checks[0]

        awaitable_status = 200
        awaitable_checks_len = 1
        awaitable_check_status = "unique"

        assert user.agency_id == repres.agency_id
        assert response_status == awaitable_status
        assert len(checks) == awaitable_checks_len
        assert check.status.value == awaitable_check_status

        response = await client.post("/users/represes/check", data=dumps(payload), headers=headers)
        response_status = response.status_code

        checks = await check_repo.list({"agency_id": repres.agency_id})
        check = checks[0]

        awaitable_status = 200
        awaitable_checks_len = 1
        awaitable_check_status = "unique"

        assert user.agency_id == repres.agency_id
        assert response_status == awaitable_status
        assert len(checks) == awaitable_checks_len
        assert check.status.value == awaitable_check_status

    async def test_not_unique(
        self, client, repres, mocker, user_repo, check_repo, repres_authorization, user
    ):
        check_mock = mocker.patch("src.users.api.user.services.CheckUniqueService.__call__")
        check_mock.return_value = False

        checks = await check_repo.list({"agency_id": repres.agency_id})

        assert not checks

        headers = {"Authorization": repres_authorization}
        payload = {
            "name": "test",
            "phone": "+70000000000",
            "email": "lkio@gmail.com",
            "surname": "test",
            "patronymic": "test",
        }

        response = await client.post("/users/represes/check", data=dumps(payload), headers=headers)
        response_status = response.status_code
        response_json = response.json()

        response_check_status = response_json["status"]["value"]

        checks = await check_repo.list({"agency_id": repres.agency_id})

        awaitable_status = 200
        awaitable_checks_len = 1
        awaitable_check_status = "not_unique"

        assert response_status == awaitable_status
        assert len(checks) == awaitable_checks_len
        assert response_check_status == awaitable_check_status


@mark.asyncio
class TestAdminsAgentsUsersRetrieveView(object):
    async def test_success(
        self,
        client,
        agent,
        repres,
        booking,
        property,
        user_repo,
        user_factory,
        booking_repo,
        check_factory,
        admin_authorization,
    ):
        user = await user_factory(agency_id=repres.agency_id)
        await check_factory(agent_id=agent.id, user_id=user.id)
        await booking_repo.update(booking, {"user_id": user.id, "agency_id": repres.agency_id})
        await user_repo.add_m2m(user, "interested", [property])

        headers = {"Authorization": admin_authorization}

        response = await client.get(f"/users/admins/{user.id}/{agent.id}", headers=headers)
        response_status = response.status_code
        response_json = response.json()
        response_indents = response_json["indents"]
        response_interesting = response_json["interesting"]

        awaitable_status = 200

        assert not response_indents
        assert not response_interesting
        assert response_status == awaitable_status

        user = await user_factory(agency_id=repres.agency_id, agent_id=agent.id)
        await check_factory(agent_id=agent.id, user_id=user.id)
        await booking_repo.update(booking, {"user_id": user.id, "agent_id": agent.id})
        await user_repo.add_m2m(user, "interested", [property])

        headers = {"Authorization": admin_authorization}

        response = await client.get(f"/users/admins/{user.id}/{agent.id}", headers=headers)
        response_status = response.status_code
        response_json = response.json()
        response_indents = response_json["indents"]
        response_interesting = response_json["interesting"]

        awaitable_status = 200

        assert response_indents
        assert response_interesting
        assert response_status == awaitable_status

    async def test_fail(
        self,
        client,
        agent,
        repres,
        booking,
        property,
        user_repo,
        user_factory,
        booking_repo,
        check_factory,
        admin_authorization,
    ):
        user = await user_factory(agency_id=repres.agency_id)
        await check_factory(agent_id=agent.id, user_id=user.id)
        await booking_repo.update(booking, {"user_id": user.id, "agency_id": repres.agency_id})
        await user_repo.add_m2m(user, "interested", [property])

        headers = {"Authorization": admin_authorization}

        response = await client.get(f"/users/admins/{user.id}/{agent.id + 1}", headers=headers)
        response_status = response.status_code
        response_json = response.json()
        response_reason = response_json["reason"]

        awaitable_status = 404
        awaitable_reason = "user_not_found"

        assert response_status == awaitable_status
        assert response_reason == awaitable_reason


@mark.asyncio
class TestRepresesUsersReboundView(object):
    async def test_success(
        self,
        client,
        repres,
        mocker,
        user_repo,
        check_repo,
        user_factory,
        check_factory,
        agent_factory,
        repres_authorization,
    ):
        mocker.patch("src.users.api.user.users_tasks.change_client_agent_task")
        to_agent = await agent_factory(agency_id=repres.agency_id)
        from_agent = await agent_factory(agency_id=repres.agency_id)
        user = await user_factory(agency_id=from_agent.agency_id, agent_id=from_agent.id)
        check = await check_factory(
            agency_id=from_agent.agency_id, agent_id=from_agent.id, user_id=user.id, status="unique"
        )

        headers = {"Authorization": repres_authorization}
        payload = {"from_agent_id": from_agent.id, "to_agent_id": to_agent.id}

        response = await client.patch(
            f"/users/represes/rebound/{user.id}", data=dumps(payload), headers=headers
        )
        response_status = response.status_code

        awaitable_status = 204

        user = await user_repo.retrieve({"id": user.id})
        check = await check_repo.retrieve({"id": check.id})

        assert response_status == awaitable_status

        assert user.agent_id == to_agent.id
        assert check.agent_id == to_agent.id

    async def test_no_agent(
        self, client, repres, user_factory, check_factory, agent_factory, repres_authorization
    ):
        to_agent = await agent_factory(agency_id=repres.agency_id)
        from_agent = await agent_factory(agency_id=repres.agency_id)
        user = await user_factory(agency_id=from_agent.agency_id, agent_id=from_agent.id)
        await check_factory(
            agency_id=from_agent.agency_id, agent_id=from_agent.id, user_id=user.id, status="unique"
        )

        headers = {"Authorization": repres_authorization}
        payload = {"from_agent_id": from_agent.id + 165, "to_agent_id": to_agent.id}

        response = await client.patch(
            f"/users/represes/rebound/{user.id}", data=dumps(payload), headers=headers
        )
        response_status = response.status_code
        response_json = response.json()
        response_reason = response_json["reason"]

        awaitable_status = 404
        awaitable_reason = "user_no_agent"

        assert response_status == awaitable_status
        assert response_reason == awaitable_reason

    async def test_not_found(
        self, client, repres, user_factory, check_factory, agent_factory, repres_authorization
    ):
        to_agent = await agent_factory(agency_id=repres.agency_id)
        from_agent = await agent_factory(agency_id=repres.agency_id)
        user = await user_factory(agency_id=from_agent.agency_id, agent_id=from_agent.id)
        await check_factory(
            agency_id=from_agent.agency_id, agent_id=from_agent.id, user_id=user.id, status="unique"
        )

        headers = {"Authorization": repres_authorization}
        payload = {"from_agent_id": from_agent.id, "to_agent_id": to_agent.id}

        response = await client.patch(
            f"/users/represes/rebound/{user.id}123", data=dumps(payload), headers=headers
        )
        response_status = response.status_code
        response_json = response.json()
        response_reason = response_json["reason"]

        awaitable_status = 404
        awaitable_reason = "user_not_found"

        assert response_status == awaitable_status
        assert response_reason == awaitable_reason

    async def test_unauthorized(
        self, client, repres, user_factory, check_factory, agent_factory, repres_authorization
    ):
        to_agent = await agent_factory(agency_id=repres.agency_id)
        from_agent = await agent_factory(agency_id=repres.agency_id)
        user = await user_factory(agency_id=from_agent.agency_id, agent_id=from_agent.id)
        await check_factory(
            agency_id=from_agent.agency_id, agent_id=from_agent.id, user_id=user.id, status="unique"
        )
        payload = {"from_agent_id": from_agent.id, "to_agent_id": to_agent.id}

        response = await client.patch(f"/users/represes/rebound/{user.id}123", data=dumps(payload))
        response_status = response.status_code

        awaitable_status = 401

        assert response_status == awaitable_status
