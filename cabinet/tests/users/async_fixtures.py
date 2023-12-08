from datetime import datetime
from uuid import uuid4

from pytz import UTC

from pytest import fixture


@fixture(scope="function")
async def user(user_repo, active_agency_1, project):
    data = {
        "email": "test_client@email.com",
        "name": "test",
        "surname": "string",
        "patronymic": "string",
        "birth_date": "2021-02-15",
        "passport_number": "123465",
        "passport_series": "9816",
        "token": str(uuid4()),
        "code_time": datetime.now(tz=UTC),
        "code": "1234",
        "is_active": False,
        "type": "client",
        "agency_id": active_agency_1.id,
        "interested_project_id": project.id,
        "maintained_id": active_agency_1.id,
    }
    user = await user_repo.update_or_create({"phone": "+79296010011"}, data)
    return user


@fixture(scope="function")
async def agent_role(user_role_repo):
    data = {
        "name": "Агент",
        "slug": "agent",
    }
    agent_role = await user_role_repo.create(data)
    return agent_role


@fixture(scope="function")
async def agent(user_repo, active_agency, project, agent_role):
    data = {
        "email": "test_agent@email.com",
        "name": "test",
        "surname": "string",
        "patronymic": "string",
        "birth_date": "2021-02-15",
        "passport_number": "123465",
        "passport_series": "9816",
        "token": str(uuid4()),
        "code_time": datetime.now(tz=UTC),
        "code": "1234",
        "is_active": False,
        "type": "agent",
        "role_id": agent_role.id,
        "agency_id": active_agency.id,
        "interested_project_id": project.id,
        "maintained_id": active_agency.id,
    }
    agent = await user_repo.update_or_create({"phone": "+79296010017"}, data)
    return agent


@fixture(scope="function")
async def agent_1(user_repo, agency_repo, project_repo, city, faker):
    project_data = {
        "slug": f"test_{faker.word()}",
        "name": faker.company(),
        "city_id": city.id,
        "address": faker.address(),
    }
    project = await project_repo.create(project_data)
    agency_data = {
        "name": faker.company(),
        "city": city,
        "type": "OAO",
        "is_approved": True,
        "inn": "222222222"
    }
    agency = await agency_repo.create(agency_data)
    data = {
        "email": "test_agent_1@mail.ru",
        "name": faker.name(),
        "surname": faker.name(),
        "patronymic": faker.name(),
        "birth_date": "2021-02-15",
        "passport_number": "123465",
        "passport_series": "9816",
        "token": str(uuid4()),
        "code_time": datetime.now(tz=UTC),
        "code": "1234",
        "is_active": False,
        "type": "agent",
        "agency_id": agency.id,
        "interested_project_id": project.id,
        "maintained_id": agency.id,
    }
    agent = await user_repo.create(data)
    return agent
