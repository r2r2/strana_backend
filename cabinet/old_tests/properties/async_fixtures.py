from copy import copy

from pytest import fixture

from src.buildings.repos import BuildingBookingTypeRepo, BuildingBookingType


@fixture(scope="function")
async def property(
    floor_repo,
    project_repo,
    property_repo,
    building_repo,
    property_data,
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
    project_data["city"]: str = project_data["city"]["slug"]

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
