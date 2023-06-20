from copy import copy

import pytest
from importlib import import_module

from src.buildings.repos import BuildingBookingTypeRepo, BuildingBookingType
from src.properties.repos import PropertyRepo


@pytest.fixture(scope="function")
def property_repo() -> PropertyRepo:
    property_repo: PropertyRepo = getattr(import_module("src.properties.repos"), "PropertyRepo")()
    return property_repo


@pytest.fixture(scope="function")
async def property(
    floor_repo,
    project_repo,
    property_repo,
    building_repo,
    property_data,
    city,
    building_booking_type_repo: BuildingBookingTypeRepo,
):
    data = copy(property_data)
    floor_data = copy(data.pop("floor"))
    project_data = copy(data.pop("project"))
    building_data = copy(data.pop("building"))

    floor_global_id = floor_data.pop("global_id", None)
    project_global_id = project_data.pop("global_id", None)
    building_global_id = building_data.pop("global_id", None)
    property_global_id = data.pop("global_id", None)
    project_data["city"]: str = city

    project = await project_repo.update_or_create({"global_id": project_global_id}, project_data)

    building_data["project"] = project
    data["project"] = project

    booking_type_data = {"id": 1, "period": 1, "price": 1}
    booking_type: BuildingBookingType = await building_booking_type_repo.update_or_create(
        data=booking_type_data, filters=dict(pk=1)
    )
    building = await building_repo.update_or_create(
        {"global_id": building_global_id}, building_data
    )
    await building.booking_types.add(booking_type)
    building = await building_repo.retrieve(
        filters=dict(id=building.id), prefetch_fields=["booking_types"]
    )

    floor_data["building"] = building
    data["building"] = building

    floor = await floor_repo.update_or_create({"global_id": floor_global_id}, floor_data)

    data["floor"] = floor

    property = await property_repo.update_or_create({"global_id": property_global_id}, data)

    setattr(property, "project", project)

    return property


@pytest.fixture(scope="function")
def property_data():
    property_data = {
        "global_id": "R2xvYmFsRmxhdFR5cGU6MQ==",
        "article": "AL30",
        "price": 4490000,
        "original_price": 4490000,
        "area": 65.69,
        "completed": True,
        "preferential_mortgage": False,
        "maternal_capital": False,
        "action": None,
        "type": "FLAT",
        "status": 0,
        "project": {
            "global_id": "R2xvYmFsUHJvamVjdFR5cGU6a3ZhcnRhbC1uYS1tb3Nrb3Zza29t",
            "name": "Квартал на Московском",
            "amocrm_name": "Квартал на Московском",
            "amocrm_enum": "1307803",
            "city_id": "7",
            "slug": "project_slug",
        },
        "building": {
            "global_id": "QnVpbGRpbmdUeXBlOjI0NDUz",
            "name": "Альфа ГП-1",
            "ready_quarter": 3,
            "built_year": 2021,
            "booking_active": True,
            "booking_period": 30,
            "booking_price": 5000,
        },
        "floor": {"global_id": "Rmxvb3JUeXBlOjYyOA==", "number": 1},
        "city": {"global_id": "Rmxvb3JUeXBlOjYyOA==", "slug": "tyumen"},
    }
    return property_data
