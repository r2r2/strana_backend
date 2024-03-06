from pytest import fixture
from importlib import import_module


@fixture(scope="function")
def agency_repo():
    agency_repo = getattr(import_module("src.agencies.repos"), "AgencyRepo")()
    return agency_repo


@fixture(scope="function")
def agency_type_repo():
    agency_type_repo = getattr(import_module("src.agencies.repos"), "AgencyGeneralTypeRepo")()
    return agency_type_repo


@fixture(scope="function")
def agency_factory(agency_repo, faker):
    async def agency(is_approved=True, i=0):
        data = {
            "inn": f"{i}{i}{i}{i}{i}{i}{i}{i}{i}",
            "name": faker.name()[:15],
            "city": faker.name()[:15],
            "is_approved": is_approved,
            "type": "OOO",
        }
        return await agency_repo.create(data=data)

    return agency
