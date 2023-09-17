import pytest
from importlib import import_module
from random import uniform

from src.properties.constants import PropertyStatuses
from src.properties.repos import PropertyRepo, Property


@pytest.fixture(scope="function")
def property_repo() -> PropertyRepo:
    property_repo: PropertyRepo = getattr(import_module("src.properties.repos"), "PropertyRepo")()
    return property_repo


@pytest.fixture(scope="function")
async def property(
    property_repo,
    project,
    building,
    faker
) -> Property:
    _property: Property = await property_repo.create(
        data=dict(
            type="FLAT",
            article="AL30",
            price=faker.random_int(min=3000000, max=11000000),
            original_price=faker.random_int(min=3000000, max=11000000),
            area=faker.pydecimal(left_digits=2, right_digits=2, positive=True),
            status=PropertyStatuses.FREE, # todo неплохо было бы генерить случайно в будущем
            rooms=faker.random_int(min=1, max=5),
            project_id=project.id,
            building_id=building.id,
            global_id=faker.pystr_format("R2xvYmFsUGFya2luZ1NwYWNlVHlwZTo4????????")
        )
    )
    return _property
