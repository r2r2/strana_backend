from pytest import fixture
from importlib import import_module


@fixture(scope="function")
def property_repo():
    property_repo = getattr(import_module("src.properties.repos"), "PropertyRepo")()
    return property_repo


@fixture(scope="function")
def import_property_service_class():
    import_property_service_class = getattr(
        import_module("src.properties.services"), "ImportPropertyService"
    )
    return import_property_service_class


@fixture(scope="function")
def property_errors_response(common_response_class):
    property_errors_response = common_response_class(
        ok=True, data=property_data, status=200, errors=True, raw=None
    )
    return property_errors_response


@fixture(scope="function")
def property_data_response(common_response_class, property_data):
    property_data_response = common_response_class(
        ok=True, data=[property_data], status=200, errors=False, raw=None
    )
    return property_data_response


@fixture(scope="function")
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
            "city": {"slug": "tyumen"},
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


@fixture(scope="function")
def property_factory(faker, property_repo):
    async def property(type="FLAT", project_id=None, building_id=None, floor_id=None, i=0):
        data = {
            "global_id": str(i),
            "project_id": project_id,
            "building_id": building_id,
            "floor_id": floor_id,
            "type": type,
        }
        return await property_repo.create(data)

    return property
