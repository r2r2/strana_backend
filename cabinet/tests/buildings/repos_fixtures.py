from importlib import import_module

from pytest import fixture

from src.buildings.repos import BuildingBookingTypeRepo, BuildingBookingType, BuildingRepo, Building


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
