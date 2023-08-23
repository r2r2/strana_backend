from importlib import import_module

from pytest import fixture

from src.buildings.repos import BuildingBookingTypeRepo, BuildingBookingType, BuildingRepo, Building
from src.projects.repos import Project


@fixture(scope="function")
def building_repo():
    building_repo = getattr(import_module("src.buildings.repos"), "BuildingRepo")()
    return building_repo


@fixture(scope="function")
def building_booking_type_repo():
    building_booking_type_repo = getattr(
        import_module("src.buildings.repos"), "BuildingBookingTypeRepo"
    )()
    return building_booking_type_repo


@fixture(scope="function")
def building_factory(
    building_repo: BuildingRepo, building_booking_type_repo: BuildingBookingTypeRepo, faker
):
    async def building(project_id=None, i=0):
        booking_type_data = {"id": i, "period": i, "price": i}
        booking_type: BuildingBookingType = await building_booking_type_repo.update_or_create(
            data=booking_type_data, filters=dict(pk=i)
        )
        await booking_type.save()
        data = {
            "project_id": project_id,
        }
        building: Building = await building_repo.create(data)
        await building.booking_types.add(booking_type)
        building = await building_repo.retrieve(
            filters=dict(id=building.id), prefetch_fields=["booking_types"]
        )
        return building

    return building


@fixture(scope="function")
async def building_booking_type(building_booking_type_repo: BuildingBookingTypeRepo):
    booking_type_data = {"id": 1, "period": 1, "price": 1}
    building_booking_type: BuildingBookingType = await building_booking_type_repo.update_or_create(
        filters=dict(pk=1), data=booking_type_data
    )
    return building_booking_type


@fixture(scope="function")
async def building(
    building_repo: BuildingRepo,
    building_booking_type: BuildingBookingType,
    faker,
    project: Project,
) -> Building:
    building: Building = await building_repo.create(
        data=dict(
            project_id=project.id,
            address=faker.address(),
            name=faker.company(),
        )
    )
    await building.booking_types.add(building_booking_type)
    await building.save()
    return building
