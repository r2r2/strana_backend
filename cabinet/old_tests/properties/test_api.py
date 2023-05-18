from json import dumps

from pytest import mark


@mark.asyncio
class TestCreatePropertyView(object):
    async def test_success(self, client, property, mocker, property_repo):
        import_mock = mocker.patch(
            "src.properties.api.property.services.ImportPropertyService.__call__"
        )
        import_mock.return_value = True, None

        await property_repo.update(property, data={"global_id": "R2xvYmFsRmxhdFR5cGU6NTIyOTc4OQ=="})

        payload = {
            "type": "FLAT",
            "global_id": "R2xvYmFsRmxhdFR5cGU6NTIyOTc4OQ==",
            "booking_type_id": 1,
        }

        response = await client.post("/properties", data=dumps(payload))
        response_status = response.status_code
        response_json = response.json()
        response_id = response_json["id"]

        awaitable_status = 201

        assert response_status == awaitable_status
        assert response_id is not None

        property = await property_repo.retrieve(
            {"id": response_id},
            related_fields=["project", "building", "floor"],
            prefetch_fields=["building__booking_types"],
        )

        assert property is not None
        assert property.building.booking_types is not None


@mark.asyncio
class TestListPropertyTypesEndpoint:
    async def test_success(self, client):
        res = await client.get("/properties/types")

        assert res.status_code == 200
        assert res.json() == [
            {"label": "Квартира", "value": "FLAT"},
            {"label": "Паркинг", "value": "PARKING"},
            {"label": "Коммерция", "value": "COMMERCIAL"},
            {"label": "Кладовка", "value": "PANTRY"},
            {"label": "Апартаменты коммерции", "value": "COMMERCIAL_APARTMENT"},
        ]
