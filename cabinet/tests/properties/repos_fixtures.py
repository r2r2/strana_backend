import pytest
from importlib import import_module

from src.properties.constants import PropertyStatuses
from src.properties.repos import PropertyRepo, Property, PropertyTypeRepo, PropertyType


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


@pytest.fixture(scope="function")
async def booked_property(
    property_repo,
    project,
    building,
    faker
) -> Property:
    _booked_roperty: Property = await property_repo.create(
        data=dict(
            type="FLAT",
            article="AL30",
            price=faker.random_int(min=3000000, max=11000000),
            original_price=faker.random_int(min=3000000, max=11000000),
            area=faker.pydecimal(left_digits=2, right_digits=2, positive=True),
            status=PropertyStatuses.BOOKED, # todo неплохо было бы генерить случайно в будущем
            rooms=faker.random_int(min=1, max=5),
            project_id=project.id,
            building_id=building.id,
            global_id=faker.pystr_format("R2xvYmFsUGFya2luZ1NwYWNlVHlwZTo4????????")
        )
    )
    return _booked_roperty


@pytest.fixture(scope="function")
def property_type_repo() -> PropertyTypeRepo:
    property_type_repo: PropertyTypeRepo = getattr(import_module("src.properties.repos"), "PropertyTypeRepo")()
    return property_type_repo


@pytest.fixture(scope="function")
async def property_type(
    property_type_repo
) -> PropertyType:
    if exist_prop_type := await property_type_repo.retrieve(filters={"slug": "flat"}):
        return exist_prop_type
    property_type = await property_type_repo.create(
        data={
            "slug": "flat",
            "label": "Квартира",
            "is_active": True,
        }
    )
    return property_type
