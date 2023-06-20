from importlib import import_module

from pytest import fixture


@fixture(scope="function")
def project_repo():
    project_repo = getattr(import_module("src.projects.repos"), "ProjectRepo")()
    return project_repo


@fixture(scope="function")
def project_factory(project_repo, faker, city):
    async def project(i=0):
        data = {"slug": f"test_{i}", "name": faker.name(), "city": city}
        return await project_repo.create(data)

    return project


@fixture(scope="function")
async def project(project_repo, faker, city):
    data = {
        "slug": f"test_{faker.word()}",
        "name": faker.company(),
        "city_id": city.id,
    }
    project_obj = await project_repo.create(data)
    return project_obj
