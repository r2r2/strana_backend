from datetime import datetime
from uuid import uuid4

from pytz import UTC
from pytest import fixture

from common import security
from src.users.constants import UserPinningStatusType, UserStatus
from src.users.repos.terms import IsConType


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
async def assigned_user(user_repo, active_agency_1, project, faker):
    data = {
        "amocrm_id": faker.random_int(min=10000000, max=99999999),
        "phone": f"+7929{faker.random_int(min=1111111, max=9999999)}",
        "email": faker.email(),
        "name": faker.name(),
        "surname": faker.name(),
        "patronymic": faker.name(),
        "birth_date": faker.date(),
        "passport_number": faker.random_int(min=100000, max=999999),
        "passport_series": faker.random_int(min=1000, max=9999),
        "token": str(uuid4()),
        "code_time": datetime.now(tz=UTC),
        "code": faker.random_int(min=1000, max=9999),
        "is_active": False,
        "type": "client",
        "agency_id": active_agency_1.id,
        "interested_project_id": project.id,
    }
    assigned_user = await user_repo.create(data)
    await assigned_user.fetch_related("agent")
    return assigned_user


@fixture(scope="function")
async def user_for_checking(user_repo, active_agency_1, project, client_role, faker):
    data = {
        "amocrm_id": faker.random_int(min=10000000, max=99999999),
        "phone": f"+7929{faker.random_int(min=1111111, max=9999999)}",
        "email": faker.email(),
        "name": faker.name(),
        "surname": faker.name(),
        "patronymic": faker.name(),
        "birth_date": faker.date(),
        "passport_number": faker.random_int(min=100000, max=999999),
        "passport_series": faker.random_int(min=1000, max=9999),
        "token": str(uuid4()),
        "code_time": datetime.now(tz=UTC),
        "code": faker.random_int(min=1000, max=9999),
        "is_active": False,
        "type": "client",
        "role_id": client_role.id,
        "agency_id": active_agency_1.id,
        "interested_project_id": project.id,
    }
    user_for_checking = await user_repo.create(data)
    await user_for_checking.fetch_related("agent")
    return user_for_checking


@fixture(scope="function")
async def user_for_checking_with_agent(user_repo, active_agency_1, agent, project, client_role, faker):
    data = {
        "amocrm_id": faker.random_int(min=10000000, max=99999999),
        "phone": f"+7929{faker.random_int(min=1111111, max=9999999)}",
        "email": faker.email(),
        "name": faker.name(),
        "surname": faker.name(),
        "patronymic": faker.name(),
        "birth_date": faker.date(),
        "passport_number": faker.random_int(min=100000, max=999999),
        "passport_series": faker.random_int(min=1000, max=9999),
        "token": str(uuid4()),
        "code_time": datetime.now(tz=UTC),
        "code": faker.random_int(min=1000, max=9999),
        "is_active": False,
        "type": "client",
        "role_id": client_role.id,
        "agent_id": agent.id,
        "agency_id": active_agency_1.id,
        "interested_project_id": project.id,
    }
    user_for_checking = await user_repo.create(data)
    await user_for_checking.fetch_related("agent")
    return user_for_checking


@fixture(scope="function")
async def user_for_checking_with_agent_agency(user_repo, active_agency, project, client_role, faker):
    data = {
        "amocrm_id": faker.random_int(min=10000000, max=99999999),
        "phone": f"+7929{faker.random_int(min=1111111, max=9999999)}",
        "email": faker.email(),
        "name": faker.name(),
        "surname": faker.name(),
        "patronymic": faker.name(),
        "birth_date": faker.date(),
        "passport_number": faker.random_int(min=100000, max=999999),
        "passport_series": faker.random_int(min=1000, max=9999),
        "token": str(uuid4()),
        "code_time": datetime.now(tz=UTC),
        "code": faker.random_int(min=1000, max=9999),
        "is_active": False,
        "type": "client",
        "role_id": client_role.id,
        "agency_id": active_agency.id,
        "interested_project_id": project.id,
    }
    user_for_checking = await user_repo.create(data)
    await user_for_checking.fetch_related("agent")
    return user_for_checking


@fixture(scope="function")
async def user_for_checking_without_phone(user_repo, active_agency_1, project, client_role, faker):
    data = {
        "amocrm_id": faker.random_int(min=10000000, max=99999999),
        "email": faker.email(),
        "name": faker.name(),
        "surname": faker.name(),
        "patronymic": faker.name(),
        "birth_date": faker.date(),
        "passport_number": faker.random_int(min=100000, max=999999),
        "passport_series": faker.random_int(min=1000, max=9999),
        "token": str(uuid4()),
        "code_time": datetime.now(tz=UTC),
        "code": faker.random_int(min=1000, max=9999),
        "is_active": False,
        "type": "client",
        "role_id": client_role.id,
        "agency_id": active_agency_1.id,
        "interested_project_id": project.id,
    }
    user_for_checking = await user_repo.create(data)
    await user_for_checking.fetch_related("agent")
    return user_for_checking


@fixture(scope="function")
async def assigned_user_with_old_agent(user_repo, active_agency_1, project, faker, agent_1):
    data = {
        "amocrm_id": faker.random_int(min=10000000, max=99999999),
        "phone": f"+7929{faker.random_int(min=1111111, max=9999999)}",
        "email": faker.email(),
        "name": faker.name(),
        "surname": faker.name(),
        "patronymic": faker.name(),
        "birth_date": faker.date(),
        "passport_number": faker.random_int(min=100000, max=999999),
        "passport_series": faker.random_int(min=1000, max=9999),
        "token": str(uuid4()),
        "code_time": datetime.now(tz=UTC),
        "code": faker.random_int(min=1000, max=9999),
        "is_active": False,
        "type": "client",
        "agent_id": agent_1.id,
        "agency_id": active_agency_1.id,
        "interested_project_id": project.id,
    }
    assigned_user = await user_repo.create(data)
    await assigned_user.fetch_related("agent")
    return assigned_user


@fixture(scope="function")
async def client_role(user_role_repo):
    data = {
        "name": "Клиент",
        "slug": "client",
    }
    client_role = await user_role_repo.create(data)
    return client_role


@fixture(scope="function")
async def agent_role(user_role_repo):
    data = {"name": "Агент"}
    agent_role = await user_role_repo.update_or_create(
        filters={"slug": "agent"},
        data=data,
    )
    return agent_role


@fixture(scope="function")
async def repres_role(user_role_repo):
    data = {
        "name": "Агент",
        "slug": "repres",
    }
    repres_role = await user_role_repo.create(data)
    return repres_role


@fixture(scope="function")
async def agent(user_repo, active_agency, project, agent_role, faker):
    data = {
        "email": "test_agent@email.com",
        "amocrm_id": faker.random_int(min=10000000, max=99999999),
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
        "role_id": agent_role.id,
        "agency_id": active_agency.id,
        "interested_project_id": project.id,
        "maintained_id": active_agency.id,
        "password": security.get_hasher().hash("12345678"),
        "is_approved": True,
    }
    agent = await user_repo.update_or_create({"phone": "+79296010017", "type": "agent"}, data)
    return agent


@fixture(scope="function")
async def agency_general_type(general_type_repo):
    data = {
        "sort": 0,
        "label": "Агентство",
    }
    general_type = await general_type_repo.update_or_create({"slug": "agency"}, data)
    return general_type


@fixture(scope="function")
async def agent_not_approved(user_repo, active_agency, project, agent_role, faker):
    data = {
        "email": "test_agent22@email.com",
        "amocrm_id": faker.random_int(min=10000000, max=99999999),
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
        "password": security.get_hasher().hash("12345678"),
        "is_approved": False,
    }
    agent = await user_repo.update_or_create({"phone": "+79296010057"}, data)
    return agent


@fixture(scope="function")
async def agent_for_deleting(user_repo, active_agency, project, agent_role, faker):
    data = {
        "email": faker.email(),
        "amocrm_id": faker.random_int(min=10000000, max=99999999),
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
        "password": security.get_hasher().hash("12345678"),
        "is_approved": False,
        "is_deleted": True,
    }
    agent = await user_repo.update_or_create({"phone": "+79296012357"}, data)
    return agent


@fixture(scope="function")
async def agent_with_user_phone(user_repo, active_agency_1, project, agent_role, user_for_checking, faker):
    data = {
        "amocrm_id": faker.random_int(min=10000000, max=99999999),
        "phone": user_for_checking.phone,
        "email": faker.email(),
        "name": faker.name(),
        "surname": faker.name(),
        "patronymic": faker.name(),
        "birth_date": faker.date(),
        "passport_number": faker.random_int(min=100000, max=999999),
        "passport_series": faker.random_int(min=1000, max=9999),
        "token": str(uuid4()),
        "code_time": datetime.now(tz=UTC),
        "code": faker.random_int(min=1000, max=9999),
        "is_active": False,
        "type": "agent",
        "role_id": agent_role.id,
        "agency_id": active_agency_1.id,
        "interested_project_id": project.id,
    }
    user_for_checking = await user_repo.create(data)
    await user_for_checking.fetch_related("agent")
    return user_for_checking


@fixture(scope="function")
async def repres_for_assign(repres_repo, active_agency, repres_role, faker):
    data = {
        "name": "test",
        "amocrm_id": faker.random_int(min=10000000, max=99999999),
        "type": "repres",
        "is_active": True,
        "surname": "string",
        "is_approved": True,
        "patronymic": "string",
        "email": "testtest_email@email.com",
        "role_id": repres_role.id,
        "duty_type": "director",
        "agency_id": active_agency.id,
    }
    repres = await repres_repo.update_or_create({"phone": "+79296010035"}, data)
    return repres


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


@fixture(scope="function")
async def consultation_type(consultation_type_repo, faker):
    consultation_type = await consultation_type_repo.update_or_create(
        filters=dict(slug="consultation_type_for_assign"),
        data={"name": faker.word()},
    )
    return consultation_type


@fixture(scope="function")
async def unique_status_partially_pinned(unique_status_repo, faker):
    unique_status = await unique_status_repo.create(
        data={
            "title": faker.word(),
            "icon": faker.word(),
            "slug": UserPinningStatusType.PARTIALLY_PINNED,
        }
    )
    return unique_status


@fixture(scope="function")
async def unique_status_pinned(unique_status_repo, faker):
    unique_status = await unique_status_repo.create(
        data={
            "title": faker.word(),
            "icon": faker.word(),
            "slug": UserPinningStatusType.PINNED,
        }
    )
    return unique_status


@fixture(scope="function")
async def unique_status_unique(unique_status_repo, faker):
    unique_status = await unique_status_repo.create(
        data={
            "title": faker.word(),
            "icon": faker.word(),
            "slug": UserStatus.UNIQUE,
        }
    )
    return unique_status


@fixture(scope="function")
async def unique_status_error(unique_status_repo, faker):
    unique_status = await unique_status_repo.create(
        data={
            "title": faker.word(),
            "icon": faker.word(),
            "slug": UserStatus.ERROR,
        }
    )
    return unique_status


@fixture(scope="function")
async def unique_user_check(check_repo, unique_status_unique):
    check = await check_repo.create(
        data={"unique_status_id": unique_status_unique.id},
    )
    return check


@fixture(scope="function")
async def not_unique_user_check(check_repo, unique_status_partially_pinned):
    check = await check_repo.create(
        data={"unique_status_id": unique_status_partially_pinned.id},
    )
    return check


@fixture(scope="function")
async def user_fixed_check(check_repo, unique_status_unique, user_for_checking, faker):
    check = await check_repo.create(
        data={
            "unique_status_id": unique_status_unique.id,
            "user_id": user_for_checking.id,
            "status_fixed": True,
            "amocrm_id": faker.random_int(min=10000000, max=99999999),
            "button_slug": "test_button_slug",
        },
    )
    return check


@fixture(scope="function")
async def user_not_fixed_check(check_repo, unique_status_unique, user_for_checking, faker):
    check = await check_repo.create(
        data={
            "unique_status_id": unique_status_unique.id,
            "user_id": user_for_checking.id,
            "status_fixed": False,
            "send_admin_email": True,
            "amocrm_id": faker.random_int(min=10000000, max=99999999),
        },
    )
    return check


@fixture(scope="function")
async def user_check_without_status(check_repo, user_for_checking, faker):
    check = await check_repo.create(
        data={"user_id": user_for_checking.id},
    )
    return check


@fixture(scope="function")
async def unique_status_button(unique_status_button_repo, faker):
    unique_status_button = await unique_status_button_repo.update_or_create(
        filters={"slug": "test_button_slug"},
        data={"text": faker.word()},
    )
    return unique_status_button


@fixture(scope="function")
async def amocrm_check_log(amocrm_check_log_repo, faker):
    amocrm_check_log_repo = await amocrm_check_log_repo.create(
        data={
            "route": faker.word(),
            "status": faker.random_int(min=0, max=9),
        },
    )
    return amocrm_check_log_repo


@fixture(scope="function")
async def check_term_1(
    check_term_repo,
    city,
    amo_pipeline_for_assign,
    amo_status_for_assign,
    unique_status_partially_pinned,
    faker,
):
    check_term = await check_term_repo.create(data={
        "is_agent": IsConType.SKIP,
        "is_assign_agency_status": IsConType.SKIP,
        "priority": 2,
        "unique_status_id": unique_status_partially_pinned.id,
    }
    )
    await check_term.cities.add(city)
    await check_term.pipelines.add(amo_pipeline_for_assign)
    await check_term.statuses.add(amo_status_for_assign)
    return check_term


@fixture(scope="function")
async def check_term_2(
    check_term_repo,
    city,
    amo_pipeline_for_assign,
    amo_status_for_assign,
    unique_status_pinned,
    faker,
):
    check_term = await check_term_repo.create(data={
        "is_agent": IsConType.YES,
        "assigned_to_agent": True,
        "is_assign_agency_status": IsConType.SKIP,
        "priority": 1,
        "unique_status_id": unique_status_pinned.id,
    }
    )
    await check_term.cities.add(city)
    await check_term.pipelines.add(amo_pipeline_for_assign)
    await check_term.statuses.add(amo_status_for_assign)
    return check_term


@fixture(scope="function")
async def check_term_3(
    check_term_repo,
    city,
    amo_pipeline_for_assign,
    amo_status_for_assign,
    unique_status_partially_pinned,
    faker,
):
    check_term = await check_term_repo.create(data={
        "is_agent": IsConType.YES,
        "assigned_to_another_agent": True,
        "is_assign_agency_status": IsConType.SKIP,
        "priority": 0,
        "unique_status_id": unique_status_partially_pinned.id,
    }
    )
    await check_term.cities.add(city)
    await check_term.pipelines.add(amo_pipeline_for_assign)
    await check_term.statuses.add(amo_status_for_assign)
    return check_term
