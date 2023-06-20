from importlib import import_module

from pytest import fixture


@fixture(scope="function")
def floor_repo():
    floor_repo = getattr(import_module("src.floors.repos"), "FloorRepo")()
    return floor_repo


@fixture(scope="function")
def floor_factory(floor_repo, faker):
    async def floor(project_id=None, building_id=None, i=0):
        data = {"project_id": project_id, "building_id": building_id, "number": i}
        return await floor_repo.create(data)

    return floor
