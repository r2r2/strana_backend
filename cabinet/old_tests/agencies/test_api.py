from json import dumps

from pytest import mark

from src.agencies.repos import Agency
from src.booking.constants import BookingSubstages


@mark.asyncio
class TestAgencyExistsView(object):
    async def test_success(self, client, agency, agency_repo):
        await agency_repo.update(agency, {"is_approved": True})

        response = await client.get(f"/agencies/{agency.inn}/exists")
        response_status = response.status_code

        awaitable_status = 200

        assert response_status == awaitable_status
        assert response.json() == dict(exists=True)

    async def test_not_found(self, client, agency_repo):
        response = await client.get(f"/agencies/123098123/exists")
        response_status = response.status_code

        awaitable_status = 200

        assert response_status == awaitable_status
        assert response.json() == dict(exists=False)


@mark.asyncio
class TestAgencyRetrieveView(object):
    async def test_success(self, client, agency, agency_repo):
        await agency_repo.update(agency, {"is_approved": True})

        response = await client.get(f"/agencies/{agency.inn}")
        response_status = response.status_code

        awaitable_status = 200

        assert response_status == awaitable_status

    async def test_not_found(self, client, agency, agency_repo):
        await agency_repo.update(agency, {"is_approved": True})

        response = await client.get(f"/agencies/{agency.inn}123")
        response_status = response.status_code
        response_json = response.json()
        response_reason = response_json["reason"]

        awaitable_status = 404
        awaitable_reason = "agency_not_found"

        assert response_status == awaitable_status
        assert response_reason == awaitable_reason

    async def test_not_approved(self, client, agency, agency_repo):
        response = await client.get(f"/agencies/{agency.inn}")
        response_status = response.status_code
        response_json = response.json()
        response_reason = response_json["reason"]

        awaitable_status = 400
        awaitable_reason = "agency_not_approved"

        assert response_status == awaitable_status
        assert response_reason == awaitable_reason


@mark.asyncio
class TestAdminsAgenciesListView(object):
    async def test_success(
        self,
        client,
        user_factory,
        agent_factory,
        agency_factory,
        repres_factory,
        admin_authorization,
        booking_factory,
        property,
    ):
        for i in range(13):
            agency = await agency_factory(i=i)
            await repres_factory(agency_id=agency.id, i=i, maintained_id=agency.id)
            for _ in range(i + 1):
                agent = await agent_factory(agency_id=agency.id)
            for _ in range(i + 2):
                user = await user_factory(agency_id=agency.id)
        await booking_factory(
            agent_id=agent.id,
            agency_id=agency.id,
            active=True,
            user_id=user.id,
            property=property,
            decremented=False,
            amocrm_substage=BookingSubstages.BOOKING,
        )
        headers = {"Authorization": admin_authorization}

        response = await client.get("/agencies/admins", headers=headers)
        response_status = response.status_code
        response_json = response.json()
        response_count = response_json["count"]
        response_info = response_json["page_info"]
        response_agency = response_json["result"][0]
        response_agents = response_agency["active_agents"]
        response_clients = response_agency["active_clients"]

        awaitable_count = 13
        awaitable_status = 200
        awaitable_agents = 13
        awaitable_clients = 1

        assert response_info["next_page"]
        assert response_count == awaitable_count
        assert response_agents == awaitable_agents
        assert response_status == awaitable_status
        assert response_clients == awaitable_clients

    async def test_search_filter(
        self,
        client,
        user_factory,
        agent_factory,
        agency_factory,
        repres_factory,
        admin_authorization,
    ):
        for i in range(13):
            agency = await agency_factory(i=i)
            await repres_factory(agency_id=agency.id, i=i, maintained_id=agency.id)
            for _ in range(i + 1):
                await agent_factory(agency_id=agency.id)
            for _ in range(i + 2):
                await user_factory(agency_id=agency.id)

        headers = {"Authorization": admin_authorization}

        search = agency.name

        response = await client.get(f"/agencies/admins?search={search}", headers=headers)
        response_status = response.status_code
        response_json = response.json()
        response_count = response_json["count"]
        response_info = response_json["page_info"]

        awaitable_count = 1
        awaitable_status = 200

        assert not response_info["next_page"]
        assert response_count == awaitable_count
        assert response_status == awaitable_status

    async def test_unauthorized(self, client):
        response = await client.get("/agencies/admins")
        response_status = response.status_code

        awaitable_status = 401

        assert response_status == awaitable_status


@mark.asyncio
class TestAdminsAgenciesRetrieveView(object):
    async def test_success(
        self, client, agent_factory, agency_factory, repres_factory, admin_authorization
    ):
        for i in range(1):
            agency = await agency_factory(i=i)
            await repres_factory(agency_id=agency.id, i=i, maintained_id=agency.id)
            for _ in range(i + 5):
                await agent_factory(agency_id=agency.id)

        headers = {"Authorization": admin_authorization}

        response = await client.get(f"/agencies/admins/{agency.id}", headers=headers)
        response_status = response.status_code

        awaitable_status = 200

        assert response_status == awaitable_status

    async def test_not_found(
        self, client, agent_factory, agency_factory, repres_factory, admin_authorization
    ):
        for i in range(1):
            agency = await agency_factory(i=i)
            await repres_factory(agency_id=agency.id, i=i, maintained_id=agency.id)
            for _ in range(i + 5):
                await agent_factory(agency_id=agency.id)

        headers = {"Authorization": admin_authorization}

        response = await client.get(f"/agencies/admins/{agency.id}12", headers=headers)
        response_status = response.status_code
        response_json = response.json()
        response_reason = response_json["reason"]

        awaitable_status = 404
        awaitable_reason = "agency_not_found"

        assert response_status == awaitable_status
        assert response_reason == awaitable_reason

    async def test_unauthorized(self, client):
        response = await client.get(f"/agencies/admins/12")
        response_status = response.status_code

        awaitable_status = 401

        assert response_status == awaitable_status


@mark.asyncio
class TestAdminsAgenciesLookupView(object):
    async def test_name_filtered(self, client, agency_factory, repres_factory, admin_authorization):
        for i in range(15):
            agency = await agency_factory(i=i)
            await repres_factory(agency_id=agency.id, i=i, maintained_id=agency.id)

        headers = {"Authorization": admin_authorization}

        response = await client.get(f"/agencies/admins/lookup?search=абзука", headers=headers)
        response_status = response.status_code
        response_json = response.json()
        response_type = response_json["type"]["value"]

        awaitable_status = 200
        awaitable_type = "name"

        assert response_status == awaitable_status
        assert response_type == awaitable_type

    async def test_phone_filtered(
        self, client, agency_factory, repres_factory, admin_authorization
    ):
        for i in range(15):
            agency = await agency_factory(i=i)
            await repres_factory(agency_id=agency.id, i=i, maintained_id=agency.id)

        headers = {"Authorization": admin_authorization}

        response = await client.get(f"/agencies/admins/lookup?search=+7234", headers=headers)
        response_status = response.status_code
        response_json = response.json()
        response_type = response_json["type"]["value"]

        awaitable_status = 200
        awaitable_type = "phone"

        assert response_status == awaitable_status
        assert response_type == awaitable_type

    async def test_email_filtered(
        self, client, agency_factory, repres_factory, admin_authorization
    ):
        for i in range(15):
            agency = await agency_factory(i=i)
            await repres_factory(agency_id=agency.id, i=i, maintained_id=agency.id)

        headers = {"Authorization": admin_authorization}

        response = await client.get(f"/agencies/admins/lookup?search=das", headers=headers)
        response_status = response.status_code
        response_json = response.json()
        response_type = response_json["type"]["value"]

        awaitable_status = 200
        awaitable_type = "email"

        assert response_status == awaitable_status
        assert response_type == awaitable_type

    async def test_unauthorized(self, client):
        response = await client.get("/agencies/admins")
        response_status = response.status_code

        awaitable_status = 401

        assert response_status == awaitable_status


@mark.asyncio
class TestAdminsAgenciesRegisterView(object):
    async def test_success(
        self, client, mocker, repres_repo, agency_repo, image_factory, admin_authorization
    ):
        mocker.patch("src.agencies.api.agency.messages.SmsService.__call__")
        mocker.patch("src.agencies.api.agency.messages.SmsService.as_task")
        mocker.patch("src.agencies.api.agency.messages.SmsService.as_future")
        mocker.patch("src.agencies.api.agency.represes_services.CreateContactService.__call__")
        mocker.patch("src.agencies.api.agency.agencies_services.CreateOrganizationService.__call__")
        files_mock = mocker.patch("src.agencies.api.agency.files.FileProcessor.__call__")
        files_mock.return_value = []

        file = image_factory("test.png")

        files = {
            "inn_files": file,
            "ogrn_files": file,
            "ogrnip_files": file,
            "charter_files": file,
            "company_files": file,
            "passport_files": file,
            "procuratory_files": file,
        }

        payload = {
            "type": "OOO",
            "city": "test",
            "inn": "535345341",
            "phone": "+79127350017",
            "email": "test@borov.com",
            "name": "test",
            "naming": "tyuio",
            "surname": "test",
            "patronymic": "test",
            "duty_type": "director",
        }

        headers = {"Authorization": admin_authorization}

        response = await client.post(
            "/agencies/admins/register", data=payload, headers=headers, files=files
        )
        response_status = response.status_code

        awaitable_status = 201

        agency = await agency_repo.retrieve({"inn": "535345341"})
        repres = await repres_repo.retrieve({"phone": "+79127350017"})

        assert agency.is_approved is True
        assert repres.is_approved is True
        assert response_status == awaitable_status

    async def test_agency_exists(self, client, repres, mocker, image_factory, admin_authorization):
        mocker.patch("src.agencies.api.agency.messages.SmsService.__call__")
        mocker.patch("src.agencies.api.agency.messages.SmsService.as_task")
        mocker.patch("src.agencies.api.agency.messages.SmsService.as_future")
        mocker.patch("src.agencies.api.agency.represes_services.CreateContactService.__call__")
        mocker.patch("src.agencies.api.agency.agencies_services.CreateOrganizationService.__call__")
        files_mock = mocker.patch("src.agencies.api.agency.files.FileProcessor.__call__")
        files_mock.return_value = []

        file = image_factory("test.png")

        files = {
            "inn_files": file,
            "ogrn_files": file,
            "ogrnip_files": file,
            "charter_files": file,
            "company_files": file,
            "passport_files": file,
            "procuratory_files": file,
        }

        payload = {
            "type": "OOO",
            "city": "test",
            "inn": "535345341",
            "phone": repres.phone,
            "email": "test@borov.com",
            "name": "test",
            "naming": "tyuio",
            "surname": "test",
            "patronymic": "test",
            "duty_type": "director",
        }

        headers = {"Authorization": admin_authorization}

        response = await client.post(
            "/agencies/admins/register", data=payload, headers=headers, files=files
        )
        response_status = response.status_code
        response_json = response.json()
        response_reason = response_json["reason"]

        awaitable_status = 400
        awaitable_reason = "agency_data_taken"

        assert response_status == awaitable_status
        assert response_reason == awaitable_reason

    async def test_deleted_agency_and_repres_are_overriden(
        self, client, repres, mocker, image_factory, admin_authorization, repres_repo, agency_repo
    ):
        mocker.patch("src.agencies.api.agency.messages.SmsService.__call__")
        mocker.patch("src.agencies.api.agency.messages.SmsService.as_task")
        mocker.patch("src.agencies.api.agency.messages.SmsService.as_future")
        mocker.patch("src.agencies.api.agency.represes_services.CreateContactService.__call__")
        mocker.patch("src.agencies.api.agency.agencies_services.CreateOrganizationService.__call__")
        files_mock = mocker.patch("src.agencies.api.agency.files.FileProcessor.__call__")
        files_mock.return_value = []

        await repres_repo.update(repres, data=dict(is_deleted=True))
        await agency_repo.update(await repres.agency, data=dict(is_deleted=True))

        file = image_factory("test.png")

        files = {
            "inn_files": file,
            "ogrn_files": file,
            "ogrnip_files": file,
            "charter_files": file,
            "company_files": file,
            "passport_files": file,
            "procuratory_files": file,
        }

        payload = {
            "type": "OOO",
            "city": "test",
            "inn": "535345341",
            "phone": repres.phone,
            "email": "test@borov.com",
            "name": "test",
            "naming": "tyuio",
            "surname": "test",
            "patronymic": "test",
            "duty_type": "director",
        }

        headers = {"Authorization": admin_authorization}

        response = await client.post(
            "/agencies/admins/register", data=payload, headers=headers, files=files
        )
        assert response.status_code == 201

    async def test_repres_exists(self, client, agency, mocker, image_factory, admin_authorization):
        mocker.patch("src.agencies.api.agency.messages.SmsService.__call__")
        mocker.patch("src.agencies.api.agency.messages.SmsService.as_task")
        mocker.patch("src.agencies.api.agency.messages.SmsService.as_future")
        mocker.patch("src.agencies.api.agency.represes_services.CreateContactService.__call__")
        mocker.patch("src.agencies.api.agency.agencies_services.CreateOrganizationService.__call__")
        files_mock = mocker.patch("src.agencies.api.agency.files.FileProcessor.__call__")
        files_mock.return_value = []

        file = image_factory("test.png")

        files = {
            "inn_files": file,
            "ogrn_files": file,
            "ogrnip_files": file,
            "charter_files": file,
            "company_files": file,
            "passport_files": file,
            "procuratory_files": file,
        }

        payload = {
            "type": "OOO",
            "city": "test",
            "inn": agency.inn,
            "phone": "+79127350017",
            "email": "test@borov.com",
            "name": "test",
            "naming": "tyuio",
            "surname": "test",
            "patronymic": "test",
            "duty_type": "director",
        }

        headers = {"Authorization": admin_authorization}

        response = await client.post(
            "/agencies/admins/register", data=payload, headers=headers, files=files
        )
        response_status = response.status_code
        response_json = response.json()
        response_reason = response_json["reason"]

        awaitable_status = 400
        awaitable_reason = "agency_data_taken"

        assert response_status == awaitable_status
        assert response_reason == awaitable_reason

    async def test_unauthorized(self, client):
        payload = {
            "type": "OOO",
            "city": "test",
            "inn": "535345341",
            "phone": "+79127350017",
            "email": "test@borov.com",
            "name": "test",
            "naming": "tyuio",
            "surname": "test",
            "patronymic": "test",
            "duty_type": "director",
        }

        response = await client.post("/agencies/admins/register", data=payload)
        response_status = response.status_code

        awaitable_status = 401

        assert response_status == awaitable_status


@mark.asyncio
class TestAdminsAgenciesApprovalView(object):
    async def test_success(
        self, client, mocker, agency, repres, repres_repo, agency_repo, admin_authorization
    ):
        mocker.patch("src.agencies.api.agency.represes_services.CreateContactService.__call__")
        mocker.patch("src.agencies.api.agency.agencies_services.CreateOrganizationService.__call__")
        await repres_repo.update(repres, {"maintained_id": agency.id, "is_approved": False})

        payload = {"is_approved": True}
        headers = {"Authorization": admin_authorization}

        response = await client.patch(
            f"/agencies/admins/approval/{agency.id}", data=dumps(payload), headers=headers
        )
        response_status = response.status_code

        awaitable_status = 204

        repres = await repres_repo.retrieve({"id": repres.id})
        agency = await agency_repo.retrieve({"id": agency.id})

        assert repres.is_approved is True
        assert agency.is_approved is True
        assert response_status == awaitable_status

    async def test_not_found(
        self, client, mocker, agency, repres, repres_repo, admin_authorization
    ):
        mocker.patch("src.agencies.api.agency.represes_services.CreateContactService.__call__")
        mocker.patch("src.agencies.api.agency.agencies_services.CreateOrganizationService.__call__")
        await repres_repo.update(repres, {"maintained_id": agency.id, "is_approved": False})

        payload = {"is_approved": True}
        headers = {"Authorization": admin_authorization}

        response = await client.patch(
            f"/agencies/admins/approval/{agency.id}12", data=dumps(payload), headers=headers
        )
        response_status = response.status_code
        response_json = response.json()
        response_reason = response_json["reason"]

        awaitable_status = 404
        awaitable_reason = "agency_not_found"

        assert response_status == awaitable_status
        assert response_reason == awaitable_reason

    async def test_unauthorized(self, client, agency):
        payload = {"is_approved": True}

        response = await client.patch(f"/agencies/admins/approval/{agency.id}", data=dumps(payload))
        response_status = response.status_code

        awaitable_status = 401

        assert response_status == awaitable_status


@mark.asyncio
class TestAdminsAgenciesSpecsView(object):
    async def test_success(self, client, admin_authorization):
        headers = {"Authorization": admin_authorization}

        response = await client.get("/agencies/admins/specs", headers=headers)
        response_status = response.status_code

        awaitable_status = 200

        assert response_status == awaitable_status

    async def test_unauthorized(self, client):

        response = await client.get("/agencies/admins/specs")
        response_status = response.status_code

        awaitable_status = 401

        assert response_status == awaitable_status


@mark.asyncio
class TestAdminsAgenciesUpdateView(object):
    async def test_success(self, client, mocker, repres, active_agency, admin_authorization, faker):
        mocker.patch("src.agencies.api.agency.messages.SmsService.__call__")
        mocker.patch("src.agencies.api.agency.messages.SmsService.as_task")
        mocker.patch("src.agencies.api.agency.messages.SmsService.as_future")
        mocker.patch("src.agencies.api.agency.email.EmailService.__call__")
        mocker.patch("src.agencies.api.agency.email.EmailService.as_task")
        mocker.patch("src.agencies.api.agency.email.EmailService.as_future")
        headers = {"Authorization": admin_authorization}
        payload = {"name": faker.pystr(), "inn": str(faker.pyint()), "city": faker.pystr()}

        response = await client.patch(
            f"/agencies/admins/{active_agency.id}", json=payload, headers=headers
        )
        response_status = response.status_code

        awaitable_status = 200

        assert response_status == awaitable_status, response.json()
        assert response.json()["name"] == payload["name"]
        assert response.json()["city"] == payload["city"]
        assert response.json()["inn"] == payload["inn"]

        agency: Agency = await Agency.get(id=active_agency.id)
        assert agency
        assert agency.name == payload["name"]
        assert agency.city == payload["city"]
        assert agency.inn == payload["inn"]

    async def test_not_found(self, client, mocker, repres, active_agency, admin_authorization):
        mocker.patch("src.agencies.api.agency.messages.SmsService.__call__")
        mocker.patch("src.agencies.api.agency.messages.SmsService.as_task")
        mocker.patch("src.agencies.api.agency.messages.SmsService.as_future")
        mocker.patch("src.agencies.api.agency.email.EmailService.__call__")
        mocker.patch("src.agencies.api.agency.email.EmailService.as_task")
        mocker.patch("src.agencies.api.agency.email.EmailService.as_future")

        headers = {"Authorization": admin_authorization}
        payload = {}

        response = await client.patch(
            f"/agencies/admins/{active_agency.id}12", data=dumps(payload), headers=headers
        )
        response_status = response.status_code
        response_json = response.json()
        response_reason = response_json["reason"]

        awaitable_status = 404
        awaitable_reason = "agency_not_found"

        assert response_status == awaitable_status
        assert response_reason == awaitable_reason

    async def test_unauthorized(self, client, active_agency):
        payload = {}

        response = await client.patch(f"/agencies/admins/{active_agency.id}12", data=dumps(payload))
        response_status = response.status_code

        awaitable_status = 401

        assert response_status == awaitable_status


@mark.asyncio
class TestAdminsAgenciesDeleteView(object):
    async def test_success(
        self,
        client,
        user_repo,
        check_repo,
        agent_repo,
        repres_repo,
        agency_repo,
        user_factory,
        agent_factory,
        active_agency,
        check_factory,
        repres_factory,
        admin_authorization,
    ):
        headers = {"Authorization": admin_authorization}

        users_ids = []
        checks_ids = []
        agents_ids = []
        represes_ids = []

        for i in range(5):
            if i == 1:
                repres = await repres_factory(
                    agency_id=active_agency.id, maintained_id=active_agency.id
                )
            else:
                repres = await repres_factory(agency_id=active_agency.id)
            represes_ids.append(repres.id)
        for i in range(5):
            agent = await agent_factory(agency_id=active_agency.id)
            agents_ids.append(agent.id)
            for j in range(3):
                user = await user_factory(agency_id=active_agency.id, agent_id=agent.id)
                users_ids.append(user.id)
                check = await check_factory(
                    agency_id=active_agency.id, agent_id=agent.id, user_id=user.id
                )
                checks_ids.append(check.id)

        response = await client.delete(f"/agencies/admins/{active_agency.id}", headers=headers)
        response_status = response.status_code

        awaitable_status = 204

        users = await user_repo.list(filters={"id__in": users_ids})
        checks = await check_repo.list(filters={"id__in": checks_ids})
        agents = await agency_repo.list(filters={"id__in": agents_ids})
        represes = await repres_repo.list(filters={"id__in": represes_ids})
        agency = await agency_repo.retrieve(filters={"id": active_agency.id})

        assert not checks
        assert agency.is_deleted is True
        assert response_status == awaitable_status
        assert all(list(a.is_deleted for a in agents))
        assert all(list(r.is_deleted for r in represes))
        assert all(list(u.agent_id is None for u in users))
        assert all(list(u.agency_id is None for u in users))

    async def test_not_found(
        self,
        client,
        user_factory,
        agent_factory,
        active_agency,
        check_factory,
        repres_factory,
        admin_authorization,
    ):
        headers = {"Authorization": admin_authorization}

        users_ids = []
        checks_ids = []
        agents_ids = []
        represes_ids = []

        for i in range(5):
            if i == 1:
                repres = await repres_factory(
                    agency_id=active_agency.id, maintained_id=active_agency.id
                )
            else:
                repres = await repres_factory(agency_id=active_agency.id)
            represes_ids.append(repres.id)
        for i in range(5):
            agent = await agent_factory(agency_id=active_agency.id)
            agents_ids.append(agent.id)
            for j in range(3):
                user = await user_factory(agency_id=active_agency.id, agent_id=agent.id)
                users_ids.append(user.id)
                check = await check_factory(
                    agency_id=active_agency.id, agent_id=agent.id, user_id=user.id
                )
                checks_ids.append(check.id)

        response = await client.delete(f"/agencies/admins/{active_agency.id}12", headers=headers)
        response_status = response.status_code
        response_json = response.json()
        response_reason = response_json["reason"]

        awaitable_status = 404
        awaitable_reason = "agency_not_found"

        assert response_status == awaitable_status
        assert response_reason == awaitable_reason

    async def test_unauthorized(self, client, active_agency):
        response = await client.delete(f"/agencies/admins/{active_agency.id}")
        response_status = response.status_code

        awaitable_status = 401

        assert response_status == awaitable_status
