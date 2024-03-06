from importlib import import_module

from pytest import fixture

from src.projects.constants import ProjectStatus


@fixture(scope="function")
def project_repo():
    project_repo = getattr(import_module("src.projects.repos"), "ProjectRepo")()
    return project_repo


@fixture(scope="function")
def project_factory(project_repo, faker, city):
    async def project(i=0):
        data = {
            "slug": f"test_{i}",
            "name": faker.name(),
            "city": city,
            "address": faker.address(),
        }
        return await project_repo.create(data)

    return project


@fixture(scope="function")
async def project(project_repo, faker, city, amo_pipeline):
    data = {
        "slug": f"test_{faker.word()}",
        "name": faker.company(),
        "city_id": city.id,
        "address": faker.address(),
        "amo_pipeline_id": amo_pipeline.id,
        "discount": faker.random_int(min=3, max=10),
    }
    project_obj = await project_repo.create(data)
    return project_obj


@fixture(scope="function")
async def project_for_assign(project_repo, faker, city, amo_pipeline_for_assign):
    data = {
        "city_id": city.id,
        "address": faker.address(),
        "amo_pipeline_id": amo_pipeline_for_assign.id,
        "discount": faker.random_int(min=3, max=10),
        "amocrm_name": faker.word(),
        "status": ProjectStatus.CURRENT,
    }
    project_obj = await project_repo.update_or_create(filters=dict(name="test_project_for_assign"), data=data)
    return project_obj
