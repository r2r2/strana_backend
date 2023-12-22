from importlib import import_module

from pytest import fixture


@fixture(scope="function")
def city_repo():
    city_repo = getattr(import_module("src.cities.repos"), "CityRepo")()
    return city_repo


@fixture(scope="function")
def city_factory(city_repo, faker):
    async def city(i=0):
        data = {"slug": f"test_{i}", "name": faker.city()}
        return await city_repo.create(data)

    return city


@fixture(scope="function")
async def city(faker, city_repo):
    data = {"slug": "msk", "name": "Moskva"}
    city_obj = await city_repo.create(data)
    return city_obj
