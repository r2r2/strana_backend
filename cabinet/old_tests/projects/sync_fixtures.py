from importlib import import_module

from pytest import fixture


@fixture(scope="function")
def project_repo():
    project_repo = getattr(import_module("src.projects.repos"), "ProjectRepo")()
    return project_repo


@fixture(scope="function")
def project_factory(project_repo, faker):
    async def project(i=0):
        data = {"slug": f"test_{i}", "name": faker.name()}
        return await project_repo.create(data)

    return project
