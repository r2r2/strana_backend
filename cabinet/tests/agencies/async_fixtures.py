from pytest import fixture


@fixture(scope="function")
async def agency(agency_repo):
    data = {"city": "test", "type": "OOO"}
    agency = await agency_repo.update_or_create({"inn": "12312312312"}, data)
    return agency


@fixture(scope="function")
async def active_agency(agency_repo):
    data = {
        "city": "testtest",
        "type": "IP",
        "is_approved": True,
        "name": "Borov",
    }
    active_agency = await agency_repo.update_or_create({"inn": "111111111"}, data)
    return active_agency
