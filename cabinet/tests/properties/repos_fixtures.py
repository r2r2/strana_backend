import pytest
from importlib import import_module

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
) -> Property:
    property: Property = await property_repo.create(
        data=dict(
            type="FLAT",
            article="AL30",
            price=4490000,
            original_price=4490000,
            area=65.69,
            status=PropertyStatuses.FREE,
            rooms=2,
            project_id=project.id,
            building_id=building.id,
        )
    )
    return property
