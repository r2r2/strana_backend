from pytest import fixture


@fixture(scope="function")
async def agency(agency_repo, city):
    data = {"city": city, "type": "OOO"}
    agency = await agency_repo.update_or_create({"inn": "12312312312"}, data)
    return agency


@fixture(scope="function")
async def active_agency(agency_repo, city, faker):
    data = {
        "amocrm_id": faker.random_int(min=10000000, max=99999999),
        "city": city,
        "type": "IP",
        "is_approved": True,
        "name": "Borov",
    }
    active_agency = await agency_repo.update_or_create({"inn": "111111111"}, data)
    return active_agency


@fixture(scope="function")
async def agency_for_deleting(agency_repo, city, faker):
    data = {
        "amocrm_id": faker.random_int(min=10000000, max=99999999),
        "city": city,
        "type": "IP",
        "is_approved": True,
        "name": faker.name(),
        "is_deleted": True,
    }
    active_agency = await agency_repo.update_or_create({"inn": "1213121244"}, data)
    return active_agency


@fixture(scope="function")
async def active_agency_1(agency_repo, city, faker):
    data = {
        "city": city,
        "type": "IP",
        "is_approved": True,
        "name": faker.company(),
    }
    active_agency = await agency_repo.update_or_create({"inn": "123123123"}, data)
    return active_agency


@fixture(scope="function")
async def agency_type(agency_type_repo, faker):
    data = {"label": faker.name()}
    agency_type = await agency_type_repo.update_or_create({"slug": "agency"}, data)
    return agency_type
