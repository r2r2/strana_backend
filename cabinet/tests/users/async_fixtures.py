from datetime import datetime
from uuid import uuid4

from pytz import UTC

from pytest import fixture


@fixture(scope="function")
async def user(user_repo, active_agency, project):
    data = {
        "email": "test_email@email.com",
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
        "agency_id": active_agency.id,
        "interested_project_id": project.id,
        "maintained_id": active_agency.id,
    }
    user = await user_repo.update_or_create({"phone": "+79296010017"}, data)
    return user


@fixture(scope="function")
async def agent(user_repo, active_agency, project):
    data = {
        "email": "test_email@email.com",
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
        "agency_id": active_agency.id,
        "interested_project_id": project.id,
        "maintained_id": active_agency.id,
    }
    agent = await user_repo.update_or_create({"phone": "+79296010017"}, data)
    return agent
